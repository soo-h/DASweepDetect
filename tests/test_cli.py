"""Tests for the public DASDC argument parser."""

import subprocess
import unittest
from unittest.mock import patch

from dasdc.cli import build_parser, main


class CliTests(unittest.TestCase):
    def test_calc_domain_defaults_to_eight_cores(self):
        args = build_parser().parse_args(
            ["calc_domain", "-i", "simu_data", "-o", "simu_feature"]
        )

        self.assertEqual(args.command, "calc_domain")
        self.assertEqual(args.core, 8)
        self.assertEqual(args.snp_filter, 250)

    def test_calc_target_accepts_region_and_window_options(self):
        args = build_parser().parse_args(
            [
                "calc_target",
                "-i",
                "chr1.vcf.gz",
                "--start",
                "100",
                "--end",
                "200",
                "--window-step",
                "50000",
                "-o",
                "features",
            ]
        )

        self.assertEqual(args.start, 100)
        self.assertEqual(args.end, 200)
        self.assertEqual(args.window_step, 50000)

    def test_training_defaults_to_tensorflow_backend(self):
        args = build_parser().parse_args(
            [
                "train",
                "--train-data",
                "train.npy",
                "--train-label",
                "train-label.npy",
                "--valid-data",
                "valid.npy",
                "--valid-label",
                "valid-label.npy",
                "--test-data",
                "test.npy",
                "--test-label",
                "test-label.npy",
                "--target",
                "target.npy",
                "-o",
                "models",
            ]
        )

        self.assertEqual(args.backend, "tensorflow")
        self.assertEqual(args.device, "cuda")
        self.assertEqual(args.epochs, 50)
        self.assertTrue(args.amp)

    def test_prediction_accepts_pytorch_backend(self):
        args = build_parser().parse_args(
            [
                "pred",
                "--backend",
                "pytorch",
                "--device",
                "cuda:1",
                "-m",
                "models",
                "-M",
                "5",
                "-f",
                "features.npy",
                "-p",
                "positions.txt",
                "-o",
                "predictions.txt",
            ]
        )

        self.assertEqual(args.backend, "pytorch")
        self.assertEqual(args.device, "cuda:1")

    @patch("dasdc.cli.run_stage", return_value=0)
    def test_main_dispatches_to_runner(self, run_stage):
        result = main(["simu", "-i", "config", "-o", "output"])

        self.assertEqual(result, 0)
        run_stage.assert_called_once()
        self.assertEqual(run_stage.call_args.args[0].command, "simu")

    @patch(
        "dasdc.cli.run_stage",
        side_effect=subprocess.CalledProcessError(7, ["legacy-script"]),
    )
    def test_main_returns_legacy_exit_status(self, _run_stage):
        result = main(
            ["calc_domain", "-i", "simu_data", "-o", "simu_feature"]
        )

        self.assertEqual(result, 7)


if __name__ == "__main__":
    unittest.main()
