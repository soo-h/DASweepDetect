"""Public command-line interface for the DASDC pipeline."""

import argparse
import subprocess
import sys
from typing import List, Optional

from . import __version__
from .runner import RunnerError, run_stage


DESCRIPTION = "DASDC: Domain Adversarial Sweep Detection and Classification"


def _add_input_output(parser: argparse.ArgumentParser, input_help: str) -> None:
    parser.add_argument("-i", "--input", required=True, help=input_help)
    parser.add_argument("-o", "--out", required=True, help="Output path")


def build_parser() -> argparse.ArgumentParser:
    """Create the package CLI parser."""

    parser = argparse.ArgumentParser(
        prog="dasdc",
        description=DESCRIPTION,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version="DASDC v{}".format(__version__),
    )
    subparsers = parser.add_subparsers(dest="command", metavar="COMMAND")
    subparsers.required = True

    simu = subparsers.add_parser(
        "simu",
        help="step 1: simulate training data with discoal",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    simu.add_argument(
        "-i",
        "--config_file",
        "--config-file",
        dest="config_file",
        required=True,
        help="Simulation configuration file, directory, or comma-separated files",
    )
    simu.add_argument("-o", "--out", required=True, help="Simulation output path")

    domain = subparsers.add_parser(
        "calc_domain",
        help="step 2: extract simulated-domain features",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    _add_input_output(
        domain, "ms-style input file, directory, or comma-separated files"
    )
    domain.add_argument(
        "--filter",
        dest="snp_filter",
        type=int,
        default=250,
        help="Minimum SNP count",
    )
    domain.add_argument("--core", type=int, default=8, help="Number of CPU cores")

    target = subparsers.add_parser(
        "calc_target",
        help="step 3: extract target-domain VCF features",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    _add_input_output(
        target, "VCF/VCF.GZ file, directory, or comma-separated files"
    )
    target.add_argument(
        "--filter",
        dest="snp_filter",
        type=int,
        default=250,
        help="Minimum SNP count",
    )
    target.add_argument("--core", type=int, default=8, help="Number of CPU cores")
    target.add_argument("--start", type=int, default=None, help="Region start position")
    target.add_argument("--end", type=int, default=None, help="Region end position")
    target.add_argument("--window-size", type=int, default=1000000, help="Window size")
    target.add_argument(
        "--window-step",
        type=int,
        default=None,
        help="Window step; defaults to 1/20 of window size",
    )

    annotation = subparsers.add_parser(
        "data_annotation",
        help="step 4: label simulated feature maps",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    _add_input_output(
        annotation, "Feature-map file, directory, or comma-separated files"
    )
    annotation.add_argument("--config", required=True, help="Label configuration file")

    train = subparsers.add_parser(
        "train",
        help="step 5: train a domain-adaptive ensemble",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    train.add_argument("--train-data", required=True, help="Training feature array")
    train.add_argument("--train-label", required=True, help="Training label array")
    train.add_argument("--valid-data", required=True, help="Validation feature array")
    train.add_argument("--valid-label", required=True, help="Validation label array")
    train.add_argument("--test-data", required=True, help="Test feature array")
    train.add_argument("--test-label", required=True, help="Test label array")
    train.add_argument(
        "-t",
        "--target",
        required=True,
        help="Target feature file, directory, or comma-separated files",
    )
    train.add_argument(
        "-M", dest="models", type=int, default=5, help="Number of ensemble models"
    )
    train.add_argument(
        "-s",
        "--save",
        type=int,
        choices=(0, 1),
        default=0,
        help="Whether to keep intermediate models",
    )
    train.add_argument(
        "--backend",
        choices=("tensorflow", "pytorch"),
        default="tensorflow",
        help="Training backend",
    )
    train.add_argument(
        "--device",
        default="cuda",
        help="PyTorch device, for example cuda, cuda:1, cpu, or auto",
    )
    train.add_argument(
        "--epochs", type=int, default=50, help="PyTorch maximum training epochs"
    )
    train.add_argument(
        "--batch-size", type=int, default=32, help="PyTorch batch size"
    )
    train.add_argument(
        "--learning-rate",
        type=float,
        default=1e-2,
        help="PyTorch SGD learning rate",
    )
    train.add_argument(
        "--patience",
        type=int,
        default=5,
        help="PyTorch early-stopping patience",
    )
    train.add_argument("--seed", type=int, default=42, help="PyTorch random seed")
    train.add_argument(
        "--workers", type=int, default=0, help="PyTorch DataLoader workers"
    )
    train_amp = train.add_mutually_exclusive_group()
    train_amp.add_argument(
        "--amp", dest="amp", action="store_true", help="Enable CUDA AMP"
    )
    train_amp.add_argument(
        "--no-amp", dest="amp", action="store_false", help="Disable CUDA AMP"
    )
    train.set_defaults(amp=True)
    train.add_argument("-o", "--out", required=True, help="Model output prefix")

    pred = subparsers.add_parser(
        "pred",
        help="step 6: run ensemble prediction",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    pred.add_argument("-m", "--model", required=True, help="Ensemble model directory")
    pred.add_argument(
        "-M",
        dest="models",
        type=int,
        required=True,
        help="Number of ensemble models",
    )
    pred.add_argument("-f", "--feature", required=True, help="Target feature-map array")
    pred.add_argument("-p", "--position", required=True, help="Target position-information file")
    pred.add_argument(
        "--backend",
        choices=("tensorflow", "pytorch"),
        default="tensorflow",
        help="Prediction backend",
    )
    pred.add_argument(
        "--device",
        default="cuda",
        help="PyTorch device, for example cuda, cuda:1, cpu, or auto",
    )
    pred.add_argument(
        "--batch-size",
        type=int,
        default=256,
        help="PyTorch prediction batch size",
    )
    pred.add_argument("-o", "--out", required=True, help="Prediction output file")

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """Parse arguments and execute one DASDC stage."""

    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return run_stage(args)
    except RunnerError as exc:
        print("dasdc: error: {}".format(exc), file=sys.stderr)
        return 2
    except subprocess.CalledProcessError as exc:
        return exc.returncode if exc.returncode else 1
    except KeyboardInterrupt:
        return 130
