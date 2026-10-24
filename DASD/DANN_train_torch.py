"""Train the DASDC domain-adversarial ensemble with PyTorch."""

import argparse
import json
import math
import random
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

import numpy as np
import torch
from torch import Tensor, nn
from torch.utils.data import DataLoader, TensorDataset

from util.torch_dann import DANN, resolve_device
from util.train_utils import get_target_data_paths


NUM_CLASSES = 5
DOMAIN_LOSS_WEIGHT = 1.0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("train_data")
    parser.add_argument("train_label")
    parser.add_argument("valid_data")
    parser.add_argument("valid_label")
    parser.add_argument("test_data")
    parser.add_argument("test_label")
    parser.add_argument("target")
    parser.add_argument("models", type=int)
    parser.add_argument("save", type=int, choices=(0, 1))
    parser.add_argument("output")
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--learning-rate", type=float, default=1e-2)
    parser.add_argument("--patience", type=int, default=5)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--workers", type=int, default=0)
    amp_group = parser.add_mutually_exclusive_group()
    amp_group.add_argument("--amp", dest="amp", action="store_true")
    amp_group.add_argument("--no-amp", dest="amp", action="store_false")
    parser.set_defaults(amp=True)
    return parser


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    if hasattr(torch.backends, "cudnn"):
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False


def normalize(data: np.ndarray) -> np.ndarray:
    """Apply the feature-wise normalization used by the legacy backend."""

    data = np.asarray(data, dtype=np.float32)
    if data.ndim != 3:
        raise ValueError(
            "Expected a three-dimensional feature array, got shape {}".format(
                data.shape
            )
        )
    maximum = np.max(data, axis=(0, 2), keepdims=True)
    minimum = np.min(data, axis=(0, 2), keepdims=True)
    denominator = maximum - minimum
    normalized = np.zeros_like(data, dtype=np.float32)
    np.divide(data - minimum, denominator, out=normalized, where=denominator != 0)
    return np.nan_to_num(normalized, copy=False)


def load_labels(path: str, expected_count: int) -> np.ndarray:
    labels = np.asarray(np.load(path), dtype=np.int64).reshape(-1)
    if labels.shape[0] != expected_count:
        raise ValueError(
            "Label count {} does not match feature count {} for {}".format(
                labels.shape[0], expected_count, path
            )
        )
    if labels.size and (labels.min() < 0 or labels.max() >= NUM_CLASSES):
        raise ValueError("Labels must be integers in the range 0-4")
    return labels


def load_target_data(
    target_path: str,
    source_count: int,
    rng: np.random.Generator,
) -> np.ndarray:
    paths = sorted(get_target_data_paths(target_path))
    if not paths:
        raise ValueError("No target-domain .npy files were found")
    sample_count = max(1, 2 * source_count // len(paths))
    sampled: List[np.ndarray] = []
    for path in paths:
        data = np.load(path)
        if data.shape[0] > sample_count:
            indices = rng.choice(data.shape[0], sample_count, replace=False)
            data = data[indices]
        sampled.append(data)
    target = np.concatenate(sampled)
    if target.shape[0] < source_count:
        print("Warning: target-domain feature count is smaller than source data")
    return normalize(target)


def make_loader(
    arrays: Sequence[np.ndarray],
    batch_size: int,
    shuffle: bool,
    workers: int,
    pin_memory: bool,
    seed: int,
    drop_last: bool = False,
) -> DataLoader:
    tensors = []
    for index, array in enumerate(arrays):
        dtype = torch.float32 if index == 0 else torch.long
        tensors.append(torch.as_tensor(array, dtype=dtype))
    generator = torch.Generator()
    generator.manual_seed(seed)
    return DataLoader(
        TensorDataset(*tensors),
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=workers,
        pin_memory=pin_memory,
        drop_last=drop_last,
        generator=generator,
    )


def evaluate(
    model: DANN,
    loader: DataLoader,
    device: torch.device,
) -> Tuple[float, float]:
    model.eval()
    criterion = nn.CrossEntropyLoss(reduction="sum")
    loss_total = 0.0
    correct = 0
    sample_count = 0
    with torch.no_grad():
        for features, labels in loader:
            features = features.to(device, non_blocking=True)
            labels = labels.to(device, non_blocking=True)
            class_logits, _ = model(features, alpha=0.0)
            loss_total += criterion(class_logits, labels).item()
            correct += (class_logits.argmax(dim=1) == labels).sum().item()
            sample_count += labels.shape[0]
    if sample_count == 0:
        raise ValueError("Evaluation dataset is empty")
    return loss_total / sample_count, correct / sample_count


def cpu_state_dict(model: DANN) -> Dict[str, Tensor]:
    return {
        name: value.detach().cpu().clone()
        for name, value in model.state_dict().items()
    }


def save_checkpoint(
    path: Path,
    model: DANN,
    input_shape: Sequence[int],
    epoch: int,
    validation_accuracy: float,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(
        {
            "format_version": 1,
            "backend": "pytorch",
            "num_classes": NUM_CLASSES,
            "input_shape": list(input_shape),
            "epoch": epoch,
            "validation_accuracy": validation_accuracy,
            "state_dict": cpu_state_dict(model),
        },
        path,
    )


def train_one_model(
    model_index: int,
    output_dir: Path,
    train_data: np.ndarray,
    train_labels: np.ndarray,
    target_data: np.ndarray,
    valid_data: np.ndarray,
    valid_labels: np.ndarray,
    test_data: np.ndarray,
    test_labels: np.ndarray,
    device: torch.device,
    args: argparse.Namespace,
) -> Dict[str, float]:
    seed = args.seed + model_index
    set_seed(seed)
    actual_batch_size = min(
        args.batch_size, train_data.shape[0], target_data.shape[0]
    )
    if actual_batch_size < 2:
        raise ValueError("At least two source and target samples are required")

    pin_memory = device.type == "cuda"
    source_loader = make_loader(
        (train_data, train_labels),
        actual_batch_size,
        True,
        args.workers,
        pin_memory,
        seed,
        drop_last=True,
    )
    target_loader = make_loader(
        (target_data,),
        actual_batch_size,
        True,
        args.workers,
        pin_memory,
        seed + 1,
        drop_last=True,
    )
    valid_loader = make_loader(
        (valid_data, valid_labels),
        args.batch_size,
        False,
        args.workers,
        pin_memory,
        seed + 2,
    )
    test_loader = make_loader(
        (test_data, test_labels),
        args.batch_size,
        False,
        args.workers,
        pin_memory,
        seed + 3,
    )

    input_shape = train_data.shape[1:]
    model = DANN(num_classes=NUM_CLASSES, input_shape=input_shape).to(device)
    optimizer = torch.optim.SGD(model.parameters(), lr=args.learning_rate)
    class_criterion = nn.CrossEntropyLoss()
    domain_criterion = nn.BCEWithLogitsLoss()
    use_amp = bool(args.amp and device.type == "cuda")
    scaler = torch.cuda.amp.GradScaler(enabled=use_amp)

    model_dir = output_dir / "model_{}".format(model_index)
    model_dir.mkdir(parents=True, exist_ok=True)
    log_path = model_dir / "training.tsv"
    best_accuracy = -1.0
    best_epoch = 0
    best_state = None
    stale_epochs = 0
    step_count = min(len(source_loader), len(target_loader))
    if step_count == 0:
        raise ValueError("Training data is too small for the selected batch size")

    with log_path.open("w") as log_file:
        log_file.write(
            "epoch\tclass_loss\tdomain_loss\tvalidation_loss\t"
            "validation_accuracy\n"
        )
        for epoch in range(args.epochs):
            model.train()
            class_loss_total = 0.0
            domain_loss_total = 0.0
            source_iterator = iter(source_loader)
            target_iterator = iter(target_loader)
            for step in range(step_count):
                source_features, source_labels = next(source_iterator)
                (target_features,) = next(target_iterator)
                source_features = source_features.to(device, non_blocking=True)
                source_labels = source_labels.to(device, non_blocking=True)
                target_features = target_features.to(device, non_blocking=True)
                progress = float(step + epoch * step_count) / max(
                    args.epochs * step_count, 1
                )
                alpha = 2.0 / (1.0 + math.exp(-10.0 * progress)) - 1.0

                optimizer.zero_grad(set_to_none=True)
                with torch.cuda.amp.autocast(enabled=use_amp):
                    class_logits, source_domain_logits = model(
                        source_features, alpha=alpha
                    )
                    _, target_domain_logits = model(target_features, alpha=alpha)
                    class_loss = class_criterion(class_logits, source_labels)
                    source_domain_loss = domain_criterion(
                        source_domain_logits,
                        torch.zeros_like(source_domain_logits),
                    )
                    target_domain_loss = domain_criterion(
                        target_domain_logits,
                        torch.ones_like(target_domain_logits),
                    )
                    domain_loss = source_domain_loss + target_domain_loss
                    total_loss = class_loss + DOMAIN_LOSS_WEIGHT * domain_loss

                scaler.scale(total_loss).backward()
                scaler.step(optimizer)
                scaler.update()
                class_loss_total += class_loss.item()
                domain_loss_total += domain_loss.item()

            validation_loss, validation_accuracy = evaluate(
                model, valid_loader, device
            )
            class_loss_mean = class_loss_total / step_count
            domain_loss_mean = domain_loss_total / step_count
            line = (
                "{}\t{:.8f}\t{:.8f}\t{:.8f}\t{:.8f}\n".format(
                    epoch + 1,
                    class_loss_mean,
                    domain_loss_mean,
                    validation_loss,
                    validation_accuracy,
                )
            )
            log_file.write(line)
            log_file.flush()
            print("model {}: {}".format(model_index, line.strip()))

            if args.save:
                save_checkpoint(
                    model_dir / "checkpoints" / "epoch_{:03d}.pt".format(epoch + 1),
                    model,
                    input_shape,
                    epoch + 1,
                    validation_accuracy,
                )

            if validation_accuracy >= best_accuracy:
                best_accuracy = validation_accuracy
                best_epoch = epoch + 1
                best_state = cpu_state_dict(model)
                stale_epochs = 0
                save_checkpoint(
                    model_dir / "model.pt",
                    model,
                    input_shape,
                    best_epoch,
                    best_accuracy,
                )
            else:
                stale_epochs += 1
                if stale_epochs >= args.patience:
                    break

        if best_state is None:
            raise RuntimeError("Training completed without producing a checkpoint")
        model.load_state_dict(best_state)
        test_loss, test_accuracy = evaluate(model, test_loader, device)
        log_file.write(
            "test\tNA\tNA\t{:.8f}\t{:.8f}\n".format(
                test_loss, test_accuracy
            )
        )

    del model
    if device.type == "cuda":
        torch.cuda.empty_cache()
    return {
        "best_epoch": best_epoch,
        "validation_accuracy": best_accuracy,
        "test_loss": test_loss,
        "test_accuracy": test_accuracy,
    }


def validate_arguments(args: argparse.Namespace) -> None:
    for name in (
        "models",
        "epochs",
        "batch_size",
        "patience",
    ):
        if getattr(args, name) <= 0:
            raise ValueError("{} must be greater than zero".format(name))
    if args.learning_rate <= 0:
        raise ValueError("learning_rate must be greater than zero")
    if args.workers < 0:
        raise ValueError("workers cannot be negative")


def main(argv: Iterable[str] = None) -> int:
    args = build_parser().parse_args(argv)
    validate_arguments(args)
    device = resolve_device(args.device)
    print("PyTorch device: {}".format(device))

    train_data = normalize(np.load(args.train_data))
    valid_data = normalize(np.load(args.valid_data))
    test_data = normalize(np.load(args.test_data))
    train_labels = load_labels(args.train_label, train_data.shape[0])
    valid_labels = load_labels(args.valid_label, valid_data.shape[0])
    test_labels = load_labels(args.test_label, test_data.shape[0])
    target_data = load_target_data(
        args.target,
        train_data.shape[0],
        np.random.default_rng(args.seed),
    )

    input_shape = train_data.shape[1:]
    for name, data in (
        ("validation", valid_data),
        ("test", test_data),
        ("target", target_data),
    ):
        if data.shape[1:] != input_shape:
            raise ValueError(
                "{} feature shape {} does not match training shape {}".format(
                    name, data.shape[1:], input_shape
                )
            )

    output = Path(args.output).resolve()
    ensemble_dir = output.parent / "{}_ensemble".format(output.name)
    ensemble_dir.mkdir(parents=True, exist_ok=True)
    results = []
    for model_index in range(args.models):
        results.append(
            train_one_model(
                model_index,
                ensemble_dir,
                train_data,
                train_labels,
                target_data,
                valid_data,
                valid_labels,
                test_data,
                test_labels,
                device,
                args,
            )
        )

    metadata = {
        "backend": "pytorch",
        "format_version": 1,
        "model_count": args.models,
        "num_classes": NUM_CLASSES,
        "input_shape": list(input_shape),
        "requested_device": args.device,
        "torch_version": torch.__version__,
        "results": results,
    }
    with (ensemble_dir / "ensemble.json").open("w") as metadata_file:
        json.dump(metadata, metadata_file, indent=2)
        metadata_file.write("\n")
    print("Saved PyTorch ensemble to {}".format(ensemble_dir))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
