"""Contract tests for the optional PyTorch DANN backend."""

import unittest

try:
    import torch
except ImportError:  # pragma: no cover - depends on the optional extra
    torch = None


@unittest.skipIf(torch is None, "PyTorch is not installed")
class TorchBackendTests(unittest.TestCase):
    def test_dann_forward_shapes(self):
        from DASD.util.torch_dann import DANN

        model = DANN(num_classes=5, input_shape=(40, 40))
        class_logits, domain_logits = model(
            torch.zeros(2, 40, 40), alpha=1.0
        )

        self.assertEqual(tuple(class_logits.shape), (2, 5))
        self.assertEqual(tuple(domain_logits.shape), (2,))

    def test_gradient_reversal_negates_and_scales_gradient(self):
        from DASD.util.torch_dann import gradient_reverse

        values = torch.tensor([1.0, 2.0], requires_grad=True)
        gradient_reverse(values, alpha=0.25).sum().backward()

        torch.testing.assert_close(values.grad, torch.tensor([-0.25, -0.25]))

    def test_cuda_device_request_fails_when_cuda_is_unavailable(self):
        if torch.cuda.is_available():
            self.skipTest("CUDA is available in this environment")

        from DASD.util.torch_dann import resolve_device

        with self.assertRaisesRegex(RuntimeError, "CUDA"):
            resolve_device("cuda")


if __name__ == "__main__":
    unittest.main()
