"""Synthetic-only implementation of the frozen N2 common-phase transform."""

from __future__ import annotations

import hashlib
import struct
from dataclasses import dataclass

import numpy as np
import torch


POLICY_ID = "RC_HSG_N2_MULTIVARIATE_COMMON_PHASE_FOURIER_V1"
REPLICATES = 199
CHANNELS = 105
MIN_SAMPLES = 500
NUMPY_VERSION = "2.5.2"
SEED_PREFIX = b"RC_HSG_N2_COMMON_PHASE_V1\0SEED\0"


class N2CommonPhaseContractError(RuntimeError):
    """Raised when the frozen N2 transform contract is violated."""


@dataclass(frozen=True)
class N2TrialSurrogate:
    values: torch.Tensor
    row_key: str
    replicate_id: int
    valid_samples: int
    phase_seed_sha256: str


@dataclass(frozen=True)
class N2BatchSurrogate:
    values: torch.Tensor
    valid_samples: torch.Tensor
    mask: torch.Tensor
    row_keys: tuple[str, ...]
    replicate_id: int
    phase_seed_sha256: tuple[str, ...]


def _fail(prefix: str, check: str, row_key: str | None = None, replicate_id: object = None) -> None:
    details = [check]
    if row_key is not None:
        details.append(row_key)
    if replicate_id is not None:
        details.append(str(replicate_id))
    raise N2CommonPhaseContractError(f"{prefix}: {'|'.join(details)}")


def _validate_replicate(replicate_id: int) -> None:
    if (
        not isinstance(replicate_id, int)
        or isinstance(replicate_id, bool)
        or not 1 <= replicate_id <= REPLICATES
    ):
        _fail("N2_COMMON_PHASE_REPLICATE_INVALID", "replicate", replicate_id=replicate_id)


def _validate_row_key(row_key: str) -> bytes:
    if not isinstance(row_key, str):
        _fail("N2_COMMON_PHASE_ROW_KEY_INVALID", "type")
    try:
        encoded = row_key.encode("ascii")
    except UnicodeEncodeError:
        _fail("N2_COMMON_PHASE_ROW_KEY_INVALID", "ascii")
    parts = row_key.split("\t")
    if (
        len(parts) != 3
        or not parts[0]
        or not parts[2]
        or len(parts[1]) != 6
        or not parts[1].isdigit()
        or any(char in row_key for char in "\r\n")
    ):
        _fail("N2_COMMON_PHASE_ROW_KEY_INVALID", "canonical")
    return encoded


def _validate_tensor(values: torch.Tensor, rank: int) -> None:
    if not isinstance(values, torch.Tensor):
        _fail("N2_COMMON_PHASE_INPUT_MISMATCH", "tensor-type")
    if values.device.type != "cpu":
        _fail("N2_COMMON_PHASE_INPUT_MISMATCH", "device")
    if values.dtype != torch.float32:
        _fail("N2_COMMON_PHASE_INPUT_MISMATCH", "dtype")
    if values.ndim != rank:
        _fail("N2_COMMON_PHASE_INPUT_MISMATCH", "rank")
    if not values.is_contiguous():
        _fail("N2_COMMON_PHASE_INPUT_MISMATCH", "contiguous")
    if values.requires_grad:
        _fail("N2_COMMON_PHASE_INPUT_MISMATCH", "requires-grad")


def _seed_digest(row_key: bytes, replicate_id: int) -> bytes:
    return hashlib.sha256(
        SEED_PREFIX + struct.pack(">H", replicate_id) + b"\0" + row_key
    ).digest()


def _transform(values: torch.Tensor, row_key: str, replicate_id: int) -> N2TrialSurrogate:
    encoded_key = _validate_row_key(row_key)
    _validate_replicate(replicate_id)
    _validate_tensor(values, rank=2)
    if values.shape[0] != CHANNELS or values.shape[1] < MIN_SAMPLES:
        _fail("N2_COMMON_PHASE_INPUT_MISMATCH", "shape", row_key, replicate_id)
    if not bool(torch.isfinite(values).all()):
        _fail("N2_COMMON_PHASE_INPUT_MISMATCH", "finite", row_key, replicate_id)
    if np.__version__ != NUMPY_VERSION:
        _fail("N2_COMMON_PHASE_NUMERIC_FAILURE", "numpy-version", row_key, replicate_id)

    digest = _seed_digest(encoded_key, replicate_id)
    seed = int.from_bytes(digest[:16], "big")
    generator = np.random.Generator(np.random.PCG64(seed))
    samples = int(values.shape[1])
    original = values.numpy().astype(np.float64, copy=True)
    spectrum = np.fft.rfft(original, n=samples, axis=-1, norm="backward")
    multipliers = np.ones(spectrum.shape[-1], dtype=np.complex128)
    interior_stop = spectrum.shape[-1] - 1 if samples % 2 == 0 else spectrum.shape[-1]
    angles = generator.uniform(-np.pi, np.pi, size=max(interior_stop - 1, 0))
    multipliers[1:interior_stop] = np.cos(angles) + 1j * np.sin(angles)
    transformed = np.fft.irfft(
        spectrum * multipliers[np.newaxis, :], n=samples, axis=-1, norm="backward"
    )
    if not np.isfinite(transformed).all():
        _fail("N2_COMMON_PHASE_NUMERIC_FAILURE", "finite", row_key, replicate_id)
    output = torch.from_numpy(transformed.astype(np.float32, copy=False)).contiguous()
    if output.shape != values.shape or output.dtype != values.dtype or output.device.type != "cpu":
        _fail("N2_COMMON_PHASE_OUTPUT_FAILURE", "shape-dtype-device", row_key, replicate_id)
    return N2TrialSurrogate(
        values=output,
        row_key=row_key,
        replicate_id=replicate_id,
        valid_samples=samples,
        phase_seed_sha256=digest.hex(),
    )


class N2CommonPhaseSampler:
    """Generate deterministic multivariate common-phase Fourier surrogates."""

    def generate_unpadded(
        self,
        values: torch.Tensor,
        row_key: str,
        replicate_id: int,
    ) -> N2TrialSurrogate:
        return _transform(values, row_key, replicate_id)

    def generate_padded(
        self,
        values: torch.Tensor,
        valid_samples: torch.Tensor,
        row_keys: tuple[str, ...],
        replicate_id: int,
    ) -> N2BatchSurrogate:
        _validate_replicate(replicate_id)
        _validate_tensor(values, rank=3)
        if values.shape[0] < 1 or values.shape[1] != CHANNELS or values.shape[2] < MIN_SAMPLES:
            _fail("N2_COMMON_PHASE_INPUT_MISMATCH", "batch-shape", replicate_id=replicate_id)
        if (
            not isinstance(valid_samples, torch.Tensor)
            or valid_samples.device.type != "cpu"
            or valid_samples.dtype != torch.int64
            or valid_samples.ndim != 1
            or not valid_samples.is_contiguous()
            or valid_samples.shape[0] != values.shape[0]
        ):
            _fail("N2_COMMON_PHASE_INPUT_MISMATCH", "valid-samples", replicate_id=replicate_id)
        if not isinstance(row_keys, tuple) or len(row_keys) != values.shape[0]:
            _fail("N2_COMMON_PHASE_ROW_KEY_INVALID", "batch-count", replicate_id=replicate_id)
        for row_key in row_keys:
            _validate_row_key(row_key)
        if len(set(row_keys)) != len(row_keys):
            _fail("N2_COMMON_PHASE_ROW_KEY_INVALID", "unique", replicate_id=replicate_id)

        lengths = valid_samples.tolist()
        if any(
            not isinstance(length, int) or not MIN_SAMPLES <= length <= values.shape[2]
            for length in lengths
        ):
            _fail("N2_COMMON_PHASE_INPUT_MISMATCH", "valid-range", replicate_id=replicate_id)

        output = torch.zeros_like(values)
        seed_hashes: list[str] = []
        for index, (row_key, length) in enumerate(zip(row_keys, lengths, strict=True)):
            prefix = values[index, :, :length].contiguous()
            if not bool(torch.isfinite(prefix).all()):
                _fail("N2_COMMON_PHASE_INPUT_MISMATCH", "finite-prefix", row_key, replicate_id)
            trial = _transform(prefix, row_key, replicate_id)
            output[index, :, :length].copy_(trial.values)
            seed_hashes.append(trial.phase_seed_sha256)

        positions = torch.arange(values.shape[2], dtype=torch.int64).unsqueeze(0)
        mask = (positions < valid_samples.unsqueeze(1)).contiguous()
        if mask.dtype != torch.bool or mask.shape != (values.shape[0], values.shape[2]):
            _fail("N2_COMMON_PHASE_MASK_FAILURE", "shape", replicate_id=replicate_id)
        if any(bool(torch.count_nonzero(output[i, :, length:])) for i, length in enumerate(lengths)):
            _fail("N2_COMMON_PHASE_MASK_FAILURE", "zero-tail", replicate_id=replicate_id)
        return N2BatchSurrogate(
            values=output,
            valid_samples=valid_samples.clone().contiguous(),
            mask=mask,
            row_keys=row_keys,
            replicate_id=replicate_id,
            phase_seed_sha256=tuple(seed_hashes),
        )
