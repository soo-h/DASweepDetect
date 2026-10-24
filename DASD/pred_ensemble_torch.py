"""Run ensemble prediction for PyTorch DASDC checkpoints."""

import argparse
from pathlib import Path
from typing import Iterable, List, Tuple

import numpy as np
import torch
from torch.utils.data import DataLoader, TensorDataset

from util.torch_dann import DANN, resolve_device


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("model")
    parser.add_argument("models", type=int)
    parser.add_argument("feature")
    parser.add_argument("position")
    parser.add_argument("output")
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--batch-size", type=int, default=256)
    return parser


def normalize(data: np.ndarray) -> np.ndarray:
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


def midpoint_region(left: float, right: float) -> Tuple[int, int]:
    length = right - left
    return int(left + length * 19 / 40), int(left + length * 21 / 40)


def read_positions(path: str) -> List[str]:
    positions = []
    with open(path) as position_file:
        for line_number, line in enumerate(position_file, start=1):
            fields = line.strip().split()
            if len(fields) != 2:
                raise ValueError(
                    "Expected two position columns at {}:{}".format(
                        path, line_number
                    )
                )
            left, right = midpoint_region(float(fields[0]), float(fields[1]))
            positions.append("{}\t{}".format(left, right))
    return positions


def find_checkpoints(model_dir: Path) -> List[Path]:
    checkpoints = sorted(
        path / "model.pt"
        for path in model_dir.iterdir()
        if path.is_dir() and (path / "model.pt").is_file()
    )
    return checkpoints


def load_checkpoint(path: Path, device: torch.device):
    try:
        return torch.load(path, map_location=device, weights_only=True)
    except TypeError:  # PyTorch versions before weights_only support
        return torch.load(path, map_location=device)


def predict_checkpoint(
    checkpoint_path: Path,
    loader: DataLoader,
    device: torch.device,
    expected_shape: Tuple[int, int],
) -> np.ndarray:
    checkpoint = load_checkpoint(checkpoint_path, device)
    input_shape = tuple(int(value) for value in checkpoint["input_shape"])
    if input_shape != expected_shape:
        raise ValueError(
            "Checkpoint {} expects shape {}, received {}".format(
                checkpoint_path, input_shape, expected_shape
            )
        )
    num_classes = int(checkpoint["num_classes"])
    model = DANN(num_classes=num_classes, input_shape=input_shape).to(device)
    model.load_state_dict(checkpoint["state_dict"])
    model.eval()
    batches = []
    with torch.no_grad():
        for (features,) in loader:
            features = features.to(device, non_blocking=True)
            class_logits, _ = model(features, alpha=0.0)
            batches.append(torch.softmax(class_logits, dim=1).cpu().numpy())
    del model
    if device.type == "cuda":
        torch.cuda.empty_cache()
    return np.concatenate(batches)


def write_predictions(
    output_path: str,
    positions: List[str],
    probabilities: np.ndarray,
) -> None:
    with open(output_path, "w") as output_file:
        output_file.write("pos_left\tpos_right\tclass\tprob\tall_prob\n")
        for position, prediction in zip(positions, probabilities):
            output_file.write(
                "{}\t{}\t{}\t{}\n".format(
                    position,
                    int(np.argmax(prediction)),
                    float(np.max(prediction)),
                    ",".join(str(float(value)) for value in prediction),
                )
            )


def main(argv: Iterable[str] = None) -> int:
    args = build_parser().parse_args(argv)
    if args.models <= 0:
        raise ValueError("models must be greater than zero")
    if args.batch_size <= 0:
        raise ValueError("batch_size must be greater than zero")
    device = resolve_device(args.device)
    print("PyTorch device: {}".format(device))

    model_dir = Path(args.model)
    checkpoints = find_checkpoints(model_dir)
    if len(checkpoints) != args.models:
        raise ValueError(
            "Found {} PyTorch models in {}, expected {}".format(
                len(checkpoints), model_dir, args.models
            )
        )

    features = normalize(np.load(args.feature))
    positions = read_positions(args.position)
    if features.shape[0] != len(positions):
        raise ValueError(
            "Position count {} does not match feature count {}".format(
                len(positions), features.shape[0]
            )
        )
    loader = DataLoader(
        TensorDataset(torch.from_numpy(features)),
        batch_size=args.batch_size,
        shuffle=False,
        pin_memory=device.type == "cuda",
    )
    ensemble = None
    input_shape = tuple(int(value) for value in features.shape[1:])
    for checkpoint in checkpoints:
        probabilities = predict_checkpoint(
            checkpoint, loader, device, input_shape
        )
        if ensemble is None:
            ensemble = np.zeros_like(probabilities, dtype=np.float64)
        if probabilities.shape != ensemble.shape:
            raise ValueError("PyTorch ensemble checkpoints have incompatible outputs")
        ensemble += probabilities
    ensemble /= len(checkpoints)
    write_predictions(args.output, positions, ensemble)
    print("Saved predictions to {}".format(args.output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
