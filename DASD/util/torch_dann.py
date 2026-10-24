"""PyTorch implementation of the DASDC domain-adversarial network."""

import math
from typing import Sequence, Tuple, Union

import torch
from torch import Tensor, nn
from torch.nn import functional as functional


Pair = Union[int, Tuple[int, int]]


def _pair(value: Pair) -> Tuple[int, int]:
    if isinstance(value, tuple):
        return value
    return value, value


def _same_padding(
    size: int,
    kernel: int,
    stride: int,
    dilation: int = 1,
) -> Tuple[int, int]:
    output_size = math.ceil(size / stride)
    effective_kernel = dilation * (kernel - 1) + 1
    total = max((output_size - 1) * stride + effective_kernel - size, 0)
    return total // 2, total - total // 2


def _pad_same(
    inputs: Tensor,
    kernel_size: Pair,
    stride: Pair,
    dilation: Pair = 1,
    value: float = 0.0,
) -> Tensor:
    kernel_height, kernel_width = _pair(kernel_size)
    stride_height, stride_width = _pair(stride)
    dilation_height, dilation_width = _pair(dilation)
    top, bottom = _same_padding(
        inputs.shape[-2], kernel_height, stride_height, dilation_height
    )
    left, right = _same_padding(
        inputs.shape[-1], kernel_width, stride_width, dilation_width
    )
    if top or bottom or left or right:
        inputs = functional.pad(inputs, (left, right, top, bottom), value=value)
    return inputs


class SamePadConv2d(nn.Module):
    """Conv2d with TensorFlow-style ``padding='same'`` semantics."""

    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        kernel_size: Pair,
        stride: Pair = 1,
    ) -> None:
        super().__init__()
        self.kernel_size = _pair(kernel_size)
        self.stride = _pair(stride)
        self.conv = nn.Conv2d(
            in_channels,
            out_channels,
            kernel_size=self.kernel_size,
            stride=self.stride,
        )

    def forward(self, inputs: Tensor) -> Tensor:
        inputs = _pad_same(inputs, self.kernel_size, self.stride)
        return self.conv(inputs)


class SamePadMaxPool2d(nn.Module):
    """MaxPool2d with TensorFlow-style ``padding='same'`` semantics."""

    def __init__(self, kernel_size: Pair) -> None:
        super().__init__()
        self.kernel_size = _pair(kernel_size)

    def forward(self, inputs: Tensor) -> Tensor:
        inputs = _pad_same(
            inputs,
            self.kernel_size,
            self.kernel_size,
            value=float("-inf"),
        )
        return functional.max_pool2d(
            inputs,
            kernel_size=self.kernel_size,
            stride=self.kernel_size,
        )


class _GradientReverse(torch.autograd.Function):
    @staticmethod
    def forward(ctx, inputs: Tensor, alpha: float) -> Tensor:
        ctx.alpha = float(alpha)
        return inputs.view_as(inputs)

    @staticmethod
    def backward(ctx, gradient: Tensor):
        return -ctx.alpha * gradient, None


def gradient_reverse(inputs: Tensor, alpha: float) -> Tensor:
    """Pass values unchanged and reverse their gradients by ``alpha``."""

    return _GradientReverse.apply(inputs, alpha)


def resolve_device(requested: str) -> torch.device:
    """Resolve a requested device and reject unavailable CUDA explicitly."""

    if requested == "auto":
        requested = "cuda" if torch.cuda.is_available() else "cpu"
    try:
        device = torch.device(requested)
    except RuntimeError as exc:
        raise RuntimeError("Invalid PyTorch device: {}".format(requested)) from exc
    if device.type == "cuda":
        if not torch.cuda.is_available():
            raise RuntimeError(
                "CUDA was requested but is unavailable. Check the GPU allocation, "
                "driver, and CUDA-enabled PyTorch installation."
            )
        if device.index is not None and device.index >= torch.cuda.device_count():
            raise RuntimeError(
                "CUDA device {} is unavailable; {} visible device(s) found".format(
                    device.index, torch.cuda.device_count()
                )
            )
    return device


class FeatureExtractor(nn.Module):
    """Convolutional feature extractor matching the TensorFlow architecture."""

    def __init__(self) -> None:
        super().__init__()
        self.layers = nn.Sequential(
            SamePadConv2d(1, 256, (1, 5)),
            nn.ReLU(),
            SamePadMaxPool2d((1, 4)),
            SamePadConv2d(256, 256, (3, 1)),
            nn.ReLU(),
            SamePadMaxPool2d((2, 1)),
            SamePadConv2d(256, 128, 1),
            nn.ReLU(),
            SamePadConv2d(128, 256, (3, 3), stride=2),
            nn.ReLU(),
            SamePadConv2d(256, 128, 1),
            nn.ReLU(),
            SamePadConv2d(128, 64, 1),
            nn.ReLU(),
            SamePadConv2d(64, 128, (2, 5)),
            nn.ReLU(),
            SamePadConv2d(128, 64, 1),
            nn.ReLU(),
            SamePadMaxPool2d((2, 1)),
            SamePadConv2d(64, 32, (5, 5)),
            nn.ReLU(),
            nn.Flatten(),
        )

    def forward(self, inputs: Tensor) -> Tensor:
        return self.layers(inputs.unsqueeze(1))


class Classifier(nn.Module):
    def __init__(self, feature_count: int, num_classes: int) -> None:
        super().__init__()
        self.layers = nn.Sequential(
            nn.Linear(feature_count, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(),
            nn.Dropout(0.25),
            nn.Linear(256, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(),
            nn.Dropout(0.05),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, num_classes),
        )

    def forward(self, inputs: Tensor) -> Tensor:
        return self.layers(inputs)


class Discriminator(nn.Module):
    def __init__(self, feature_count: int) -> None:
        super().__init__()
        self.layers = nn.Sequential(
            nn.Linear(feature_count, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, 1),
        )

    def forward(self, inputs: Tensor) -> Tensor:
        return self.layers(inputs).squeeze(1)


class DANN(nn.Module):
    """Domain-adversarial classifier with a gradient-reversal branch."""

    def __init__(
        self,
        num_classes: int = 5,
        input_shape: Sequence[int] = (40, 40),
    ) -> None:
        super().__init__()
        if len(input_shape) != 2:
            raise ValueError("DANN input_shape must contain two dimensions")
        self.input_shape = tuple(int(value) for value in input_shape)
        self.num_classes = int(num_classes)
        self.feature = FeatureExtractor()
        with torch.no_grad():
            feature_count = self.feature(
                torch.zeros(1, self.input_shape[0], self.input_shape[1])
            ).shape[1]
        self.classifier = Classifier(feature_count, self.num_classes)
        self.discriminator = Discriminator(feature_count)

    def forward(self, inputs: Tensor, alpha: float = 1.0):
        features = self.feature(inputs)
        class_logits = self.classifier(features)
        domain_logits = self.discriminator(gradient_reverse(features, alpha))
        return class_logits, domain_logits
