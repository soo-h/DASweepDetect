"""Translate the package CLI into calls to the existing DASDC scripts."""

import importlib.util
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Optional


LEGACY_SCRIPTS = {
    "simu": "simudata_gen.py",
    "calc_domain": "simudata_to_feature.py",
    "calc_target": "vcf_to_featureMap.py",
    "data_annotation": "label_data.py",
    "train": "DANN_train.py",
    "pred": "pred_ensemble.py",
}


class RunnerError(RuntimeError):
    """Raised when the editable-install repository layout is unavailable."""


def repository_root() -> Path:
    """Return the repository root used by an editable installation."""

    return Path(__file__).resolve().parent.parent


def _absolute_path(value: str, cwd: Path) -> str:
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = cwd / path
    return str(path.resolve())


def _absolute_path_list(value: str, cwd: Path) -> str:
    """Resolve a legacy comma-separated file list relative to the caller."""

    paths = value.split(",")
    if any(not path.strip() for path in paths):
        raise RunnerError("path lists cannot contain empty entries")
    return ",".join(_absolute_path(path.strip(), cwd) for path in paths)


def _optional(value: Optional[int]) -> str:
    return "None" if value is None else str(value)


def build_command(
    args,
    cwd: Optional[Path] = None,
    project_root: Optional[Path] = None,
) -> List[str]:
    """Build the legacy script command represented by an argparse namespace."""

    cwd = Path.cwd() if cwd is None else Path(cwd)
    project_root = repository_root() if project_root is None else Path(project_root)

    backend = getattr(args, "backend", "tensorflow")
    try:
        script_name = LEGACY_SCRIPTS[args.command]
    except KeyError as exc:
        raise RunnerError("unknown pipeline stage: {}".format(args.command)) from exc
    if args.command == "train" and backend == "pytorch":
        script_name = "DANN_train_torch.py"
    elif args.command == "pred" and backend == "pytorch":
        script_name = "pred_ensemble_torch.py"

    script = project_root / "DASD" / script_name
    if not script.is_file():
        raise RunnerError(
            "legacy script not found at {}; install from the repository with "
            "'python3.8 -m pip install -e .'".format(script)
        )

    command = [sys.executable, str(script)]

    if args.command == "simu":
        discoal = project_root / "discoal"
        if not discoal.is_file():
            raise RunnerError("discoal executable not found at {}".format(discoal))
        if not os.access(str(discoal), os.X_OK):
            raise RunnerError(
                "discoal is not executable; run 'chmod 755 discoal' in the repository"
            )
        command.extend(
            [
                _absolute_path_list(args.config_file, cwd),
                _absolute_path(args.out, cwd),
                str(discoal),
            ]
        )
    elif args.command == "calc_domain":
        command.extend(
            [
                _absolute_path_list(args.input, cwd),
                str(args.core),
                str(args.snp_filter),
                _absolute_path(args.out, cwd),
            ]
        )
    elif args.command == "calc_target":
        command.extend(
            [
                _absolute_path_list(args.input, cwd),
                str(args.core),
                str(args.snp_filter),
                _optional(args.start),
                _optional(args.end),
                str(args.window_size),
                _optional(args.window_step),
                _absolute_path(args.out, cwd),
            ]
        )
    elif args.command == "data_annotation":
        command.extend(
            [
                _absolute_path_list(args.input, cwd),
                _absolute_path(args.config, cwd),
                _absolute_path(args.out, cwd),
            ]
        )
    elif args.command == "train":
        command.extend(
            [
                _absolute_path(args.train_data, cwd),
                _absolute_path(args.train_label, cwd),
                _absolute_path(args.valid_data, cwd),
                _absolute_path(args.valid_label, cwd),
                _absolute_path(args.test_data, cwd),
                _absolute_path(args.test_label, cwd),
                _absolute_path_list(args.target, cwd),
                str(args.models),
                str(args.save),
                _absolute_path(args.out, cwd),
            ]
        )
        if backend == "pytorch":
            command.extend(
                [
                    "--device",
                    str(args.device),
                    "--epochs",
                    str(args.epochs),
                    "--batch-size",
                    str(args.batch_size),
                    "--learning-rate",
                    str(args.learning_rate),
                    "--patience",
                    str(args.patience),
                    "--seed",
                    str(args.seed),
                    "--workers",
                    str(args.workers),
                    "--amp" if args.amp else "--no-amp",
                ]
            )
    elif args.command == "pred":
        command.extend(
            [
                _absolute_path(args.model, cwd),
                str(args.models),
                _absolute_path(args.feature, cwd),
                _absolute_path(args.position, cwd),
                _absolute_path(args.out, cwd),
            ]
        )
        if backend == "pytorch":
            command.extend(
                [
                    "--device",
                    str(args.device),
                    "--batch-size",
                    str(args.batch_size),
                ]
            )

    return command


def run_stage(args) -> int:
    """Run one legacy pipeline stage and preserve its exit status."""

    backend = getattr(args, "backend", "tensorflow")
    if args.command in ("train", "pred") and backend == "tensorflow":
        if sys.version_info >= (3, 10):
            raise RunnerError(
                "the TensorFlow 2.7 backend supports Python 3.8-3.9; "
                "use '--backend pytorch' on newer Python versions"
            )
    if args.command in ("train", "pred") and backend == "pytorch":
        if importlib.util.find_spec("torch") is None:
            raise RunnerError(
                "PyTorch is not installed; install a CUDA-enabled build from "
                "https://pytorch.org/get-started/locally/"
            )
    subprocess.run(build_command(args), check=True)
    return 0
