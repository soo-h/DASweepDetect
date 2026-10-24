"""Tests for forwarding package arguments to the legacy scripts."""

import argparse
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from dasdc.runner import RunnerError, build_command, repository_root, run_stage


class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.root = repository_root()
        self.cwd = self.root / "tests"

    def test_simulation_command_uses_current_python_and_repository_discoal(self):
        args = argparse.Namespace(command="simu", config_file="config", out="output")

        command = build_command(args, cwd=self.cwd, project_root=self.root)

        self.assertEqual(command[0], sys.executable)
        self.assertEqual(command[1], str(self.root / "DASD" / "simudata_gen.py"))
        self.assertEqual(command[2], str((self.cwd / "config").resolve()))
        self.assertEqual(command[3], str((self.cwd / "output").resolve()))
        self.assertEqual(command[4], str(self.root / "discoal"))

    def test_target_command_preserves_none_for_legacy_script(self):
        args = argparse.Namespace(
            command="calc_target",
            input="chr1.vcf.gz,chr2.vcf.gz",
            core=8,
            snp_filter=250,
            start=None,
            end=None,
            window_size=1000000,
            window_step=None,
            out="features",
        )

        command = build_command(args, cwd=self.cwd, project_root=self.root)

        self.assertEqual(
            command[2],
            ",".join(
                [
                    str((self.cwd / "chr1.vcf.gz").resolve()),
                    str((self.cwd / "chr2.vcf.gz").resolve()),
                ]
            ),
        )
        self.assertEqual(command[5:7], ["None", "None"])
        self.assertEqual(command[8], "None")

    def test_annotation_command_resolves_config_and_output_paths(self):
        args = argparse.Namespace(
            command="data_annotation",
            input="features",
            config="labels.txt",
            out="dataset",
        )

        command = build_command(args, cwd=self.cwd, project_root=self.root)

        self.assertEqual(command[2], str((self.cwd / "features").resolve()))
        self.assertEqual(command[3], str((self.cwd / "labels.txt").resolve()))
        self.assertEqual(command[4], str((self.cwd / "dataset").resolve()))

    def test_training_command_forwards_all_legacy_arguments_in_order(self):
        args = argparse.Namespace(
            command="train",
            train_data="train.npy",
            train_label="train_label.npy",
            valid_data="valid.npy",
            valid_label="valid_label.npy",
            test_data="test.npy",
            test_label="test_label.npy",
            target="target_a.npy,target_b.npy",
            models=5,
            save=0,
            out="models/ensemble",
        )

        command = build_command(args, cwd=self.cwd, project_root=self.root)

        expected_paths = [
            "train.npy",
            "train_label.npy",
            "valid.npy",
            "valid_label.npy",
            "test.npy",
            "test_label.npy",
        ]
        self.assertEqual(
            command[2:8],
            [str((self.cwd / path).resolve()) for path in expected_paths],
        )
        self.assertEqual(
            command[8],
            ",".join(
                str((self.cwd / path).resolve())
                for path in ("target_a.npy", "target_b.npy")
            ),
        )
        self.assertEqual(command[9:11], ["5", "0"])
        self.assertEqual(command[11], str((self.cwd / "models/ensemble").resolve()))

    def test_pytorch_training_command_forwards_gpu_options(self):
        args = argparse.Namespace(
            command="train",
            backend="pytorch",
            train_data="train.npy",
            train_label="train_label.npy",
            valid_data="valid.npy",
            valid_label="valid_label.npy",
            test_data="test.npy",
            test_label="test_label.npy",
            target="target.npy",
            models=3,
            save=0,
            out="models/ensemble",
            device="cuda:1",
            epochs=2,
            batch_size=16,
            learning_rate=0.005,
            patience=4,
            seed=123,
            workers=2,
            amp=False,
        )

        command = build_command(args, cwd=self.cwd, project_root=self.root)

        self.assertEqual(
            command[1], str(self.root / "DASD" / "DANN_train_torch.py")
        )
        self.assertEqual(
            command[-15:],
            [
                "--device",
                "cuda:1",
                "--epochs",
                "2",
                "--batch-size",
                "16",
                "--learning-rate",
                "0.005",
                "--patience",
                "4",
                "--seed",
                "123",
                "--workers",
                "2",
                "--no-amp",
            ],
        )

    def test_prediction_command_resolves_paths_relative_to_caller(self):
        args = argparse.Namespace(
            command="pred",
            model="models",
            models=5,
            feature="chr1.features.npy",
            position="chr1.positions",
            out="prediction.txt",
        )

        command = build_command(args, cwd=self.cwd, project_root=self.root)

        self.assertEqual(command[2], str((self.cwd / "models").resolve()))
        self.assertEqual(command[3], "5")
        self.assertEqual(
            command[4], str((self.cwd / "chr1.features.npy").resolve())
        )
        self.assertEqual(
            command[5], str((self.cwd / "chr1.positions").resolve())
        )
        self.assertEqual(
            command[6], str((self.cwd / "prediction.txt").resolve())
        )

    def test_pytorch_prediction_uses_torch_script_and_device(self):
        args = argparse.Namespace(
            command="pred",
            backend="pytorch",
            model="models",
            models=5,
            feature="chr1.features.npy",
            position="chr1.positions",
            out="prediction.txt",
            device="cuda",
            batch_size=512,
        )

        command = build_command(args, cwd=self.cwd, project_root=self.root)

        self.assertEqual(
            command[1], str(self.root / "DASD" / "pred_ensemble_torch.py")
        )
        self.assertEqual(command[-4:], ["--device", "cuda", "--batch-size", "512"])

    @patch("dasdc.runner.subprocess.run")
    def test_run_stage_checks_subprocess_exit_status(self, subprocess_run):
        args = argparse.Namespace(
            command="calc_domain",
            input="simu_data",
            core=8,
            snp_filter=250,
            out="features",
        )

        result = run_stage(args)

        self.assertEqual(result, 0)
        subprocess_run.assert_called_once_with(build_command(args), check=True)

    @patch("dasdc.runner.importlib.util.find_spec", return_value=None)
    def test_pytorch_stage_reports_missing_optional_dependency(self, _find_spec):
        args = argparse.Namespace(command="pred", backend="pytorch")

        with self.assertRaisesRegex(RunnerError, "PyTorch is not installed"):
            run_stage(args)

    @unittest.skipUnless(
        sys.version_info >= (3, 10),
        "TensorFlow version guard applies only to Python 3.10+",
    )
    def test_tensorflow_stage_rejects_unsupported_python(self):
        args = argparse.Namespace(command="train", backend="tensorflow")

        with self.assertRaisesRegex(RunnerError, "Python 3.8-3.9"):
            run_stage(args)

    @patch(
        "dasdc.runner.subprocess.run",
        side_effect=subprocess.CalledProcessError(7, ["legacy-script"]),
    )
    def test_run_stage_propagates_subprocess_failure(self, _subprocess_run):
        args = argparse.Namespace(
            command="calc_domain",
            input="simu_data",
            core=8,
            snp_filter=250,
            out="features",
        )

        with self.assertRaises(subprocess.CalledProcessError) as raised:
            run_stage(args)

        self.assertEqual(raised.exception.returncode, 7)


if __name__ == "__main__":
    unittest.main()
