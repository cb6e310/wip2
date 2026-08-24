"""Clean-room implementation of the frozen native spectral A1 interface."""

from __future__ import annotations

import math
from dataclasses import dataclass

import torch
from torch import Tensor, nn


CHANNEL_ORDER_HASH = "23b8d1ee22d87560fe1a6384141b2713c450ca34ef9eeff8241e7bd3bd885ef5"
SAMPLING_HZ = 500
UNIT_STATUS = "RELEASE_NATIVE_AMPLITUDE_UNRESOLVED"
PROCESSED_REFERENCE = "common-average"
INPUT_CHANNELS = 105
WINDOW_SAMPLES = 500
HOP_SAMPLES = 250
TOKEN_DIM = 840
EMBEDDING_DIM = 256
BANDS_HZ = ((1, 4), (4, 8), (8, 10), (10, 13), (13, 20), (20, 30), (30, 45), (55, 75))
FEATURE_EPSILON = 1.0e-12


class AInterfaceContractError(ValueError):
    """Raised when an input violates the frozen A-interface contract."""


@dataclass(frozen=True)
class NativeSpectralA1Output:
    window_embeddings: Tensor
    window_mask: Tensor
    pooled_embedding: Tensor


def _contract_error(code: str, detail: str) -> None:
    raise AInterfaceContractError(f"{code}: {detail}")


class NativeSpectralA1(nn.Module):
    """Frozen 105-channel spectral tokenizer and temporal encoder."""

    def __init__(self, init_seed: int):
        super().__init__()
        if not isinstance(init_seed, int) or isinstance(init_seed, bool):
            raise TypeError("init_seed must be an integer")

        # fork_rng restores caller state after CPU-only deterministic construction.
        with torch.random.fork_rng(devices=[]):
            torch.manual_seed(init_seed)
            self.projection = nn.Linear(TOKEN_DIM, EMBEDDING_DIM, bias=True, device="cpu")
            self.projection_activation = nn.GELU(approximate="none")
            self.projection_norm = nn.LayerNorm(EMBEDDING_DIM, eps=1.0e-5, device="cpu")
            self.projection_dropout = nn.Dropout(0.10)
            layer = nn.TransformerEncoderLayer(
                d_model=EMBEDDING_DIM,
                nhead=4,
                dim_feedforward=512,
                dropout=0.10,
                activation="gelu",
                batch_first=True,
                norm_first=True,
                device="cpu",
            )
            self.encoder = nn.TransformerEncoder(layer, num_layers=2)
            self.final_norm = nn.LayerNorm(EMBEDDING_DIM, eps=1.0e-5, device="cpu")
            self._reset_parameters()

        self.register_buffer(
            "hann_window",
            torch.hann_window(WINDOW_SAMPLES, periodic=False, dtype=torch.float32),
            persistent=True,
        )

    def _reset_parameters(self) -> None:
        for module in self.modules():
            if isinstance(module, nn.MultiheadAttention):
                nn.init.xavier_uniform_(module.in_proj_weight, gain=1.0)
                if module.in_proj_bias is not None:
                    nn.init.zeros_(module.in_proj_bias)
                if module.bias_k is not None:
                    nn.init.zeros_(module.bias_k)
                if module.bias_v is not None:
                    nn.init.zeros_(module.bias_v)
            elif isinstance(module, nn.Linear):
                nn.init.xavier_uniform_(module.weight, gain=1.0)
                if module.bias is not None:
                    nn.init.zeros_(module.bias)
            elif isinstance(module, nn.LayerNorm):
                nn.init.ones_(module.weight)
                nn.init.zeros_(module.bias)

    @staticmethod
    def _position_encoding(length: int, *, device: torch.device, dtype: torch.dtype) -> Tensor:
        positions = torch.arange(length, device=device, dtype=dtype).unsqueeze(1)
        divisor = torch.exp(
            torch.arange(0, EMBEDDING_DIM, 2, device=device, dtype=dtype)
            * (-math.log(10000.0) / EMBEDDING_DIM)
        )
        encoding = torch.zeros((length, EMBEDDING_DIM), device=device, dtype=dtype)
        encoding[:, 0::2] = torch.sin(positions * divisor)
        encoding[:, 1::2] = torch.cos(positions * divisor)
        return encoding

    def _validate(
        self,
        eeg: Tensor,
        valid_samples: Tensor,
        *,
        channel_order_hash: str,
        sampling_hz: int,
        unit_status: str,
        processed_reference: str,
    ) -> list[int]:
        if not isinstance(eeg, Tensor) or eeg.ndim != 3:
            _contract_error("A_INPUT_RANK", "eeg must have rank 3")
        if not eeg.is_floating_point():
            _contract_error("A_INPUT_DTYPE", "eeg must be floating point")
        if eeg.shape[1] != INPUT_CHANNELS:
            _contract_error("A_INPUT_CHANNELS", f"expected {INPUT_CHANNELS} channels")
        model_device = self.projection.weight.device
        if eeg.device != model_device or not isinstance(valid_samples, Tensor) or valid_samples.device != model_device:
            _contract_error("A_INPUT_DEVICE", "eeg, valid_samples, and model must share a device")
        if (
            channel_order_hash != CHANNEL_ORDER_HASH
            or sampling_hz != SAMPLING_HZ
            or unit_status != UNIT_STATUS
            or processed_reference != PROCESSED_REFERENCE
        ):
            _contract_error("A_METADATA_MISMATCH", "frozen input metadata does not match")
        integer_dtypes = {torch.uint8, torch.int8, torch.int16, torch.int32, torch.int64}
        if valid_samples.ndim != 1 or valid_samples.shape[0] != eeg.shape[0] or valid_samples.dtype not in integer_dtypes:
            _contract_error("A_VALID_SAMPLES", "valid_samples must be an integer tensor [B]")
        lengths = [int(value) for value in valid_samples.tolist()]
        if any(value < 0 or value > eeg.shape[2] for value in lengths):
            _contract_error("A_VALID_SAMPLES", "valid_samples is outside [0,T]")
        if any(value < WINDOW_SAMPLES for value in lengths):
            _contract_error("A_SHORT_SEGMENT", f"all rows require at least {WINDOW_SAMPLES} valid samples")
        for index, length in enumerate(lengths):
            if not torch.isfinite(eeg[index, :, :length]).all().item():
                _contract_error("A_NONFINITE", f"nonfinite value in valid slice at batch index {index}")
        return lengths

    def _spectral_tokens(self, trial: Tensor, valid_length: int) -> Tensor:
        signal = trial[:, :valid_length].to(dtype=torch.float32)
        centered = signal - signal.median(dim=1, keepdim=True).values
        mad = centered.abs().median(dim=1, keepdim=True).values
        rms = centered.square().mean(dim=1, keepdim=True).sqrt()
        floor = torch.full_like(mad, 1.0e-6)
        scale = torch.maximum(torch.maximum(1.4826 * mad, rms), floor)
        normalized = (centered / scale).clamp(-20.0, 20.0)

        windows = normalized.unfold(dimension=1, size=WINDOW_SAMPLES, step=HOP_SAMPLES)
        windowed = windows * self.hann_window
        spectrum = torch.fft.rfft(windowed, n=WINDOW_SAMPLES, dim=-1, norm="backward")
        power = spectrum.abs().square()
        denominator = power[..., 1:75].sum(dim=-1)
        features = [
            torch.log((power[..., low:high].sum(dim=-1) + FEATURE_EPSILON) / (denominator + FEATURE_EPSILON))
            for low, high in BANDS_HZ
        ]
        # [channels, windows, bands] -> [windows, channels * bands].
        return torch.stack(features, dim=-1).permute(1, 0, 2).reshape(windows.shape[1], TOKEN_DIM)

    def forward(
        self,
        eeg: Tensor,
        valid_samples: Tensor,
        *,
        channel_order_hash: str,
        sampling_hz: int,
        unit_status: str,
        processed_reference: str,
    ) -> NativeSpectralA1Output:
        lengths = self._validate(
            eeg,
            valid_samples,
            channel_order_hash=channel_order_hash,
            sampling_hz=sampling_hz,
            unit_status=unit_status,
            processed_reference=processed_reference,
        )
        token_rows = [self._spectral_tokens(eeg[index], length) for index, length in enumerate(lengths)]
        window_counts = [row.shape[0] for row in token_rows]
        maximum = max(window_counts)
        tokens = torch.zeros((eeg.shape[0], maximum, TOKEN_DIM), device=eeg.device, dtype=torch.float32)
        mask = torch.zeros((eeg.shape[0], maximum), device=eeg.device, dtype=torch.bool)
        for index, row in enumerate(token_rows):
            tokens[index, : row.shape[0]] = row
            mask[index, : row.shape[0]] = True

        encoded = self.projection(tokens)
        encoded = self.projection_activation(encoded)
        encoded = self.projection_norm(encoded)
        encoded = self.projection_dropout(encoded)
        encoded = encoded + self._position_encoding(maximum, device=encoded.device, dtype=encoded.dtype)
        encoded = self.encoder(encoded, src_key_padding_mask=~mask)
        encoded = self.final_norm(encoded)
        encoded = encoded.masked_fill(~mask.unsqueeze(-1), 0.0)
        pooled = encoded.sum(dim=1) / mask.sum(dim=1, keepdim=True).to(encoded.dtype)
        return NativeSpectralA1Output(encoded, mask, pooled)
