from __future__ import annotations

import hashlib
import struct
import sys
import unittest
from dataclasses import FrozenInstanceError
from pathlib import Path

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rc_hsg.references import (
    N2BatchSurrogate,
    N2CommonPhaseContractError,
    N2CommonPhaseSampler,
    N2TrialSurrogate,
)
from rc_hsg.references.n2_common_phase import SEED_PREFIX


ROW_KEY = "ZAB\t000017\tocc_fixture"
PAIR_PANEL = ((0, 1), (0, 52), (0, 104), (1, 2), (26, 78), (52, 104), (103, 104))


def analytic_fixture(samples: int) -> torch.Tensor:
    time = np.arange(samples, dtype=np.float64)
    rows = []
    for channel in range(105):
        phase = (channel + 1) * 0.013
        signal = (
            np.sin(2.0 * np.pi * 3.0 * time / samples + phase)
            + 0.37 * np.cos(2.0 * np.pi * 11.0 * time / samples - 2.0 * phase)
            + 0.11 * np.sin(2.0 * np.pi * 37.0 * time / samples + 0.5 * phase)
            + 0.017 * (((time + 3 * channel) % 29.0) / 29.0 - 0.5)
            + 0.003 * channel
        )
        signal[(channel * 17 + 5) % samples] += 0.19
        rows.append(signal)
    return torch.from_numpy(np.asarray(rows, dtype=np.float32)).contiguous()


def relative_norm(actual: np.ndarray, expected: np.ndarray, floor: float = 1e-12) -> float:
    return float(np.linalg.norm(actual - expected) / max(float(np.linalg.norm(expected)), floor))


def preservation_metrics(original: torch.Tensor, surrogate: torch.Tensor, pairs=PAIR_PANEL) -> dict[str, float]:
    x = original.numpy().astype(np.float64)
    y = surrogate.numpy().astype(np.float64)
    xf = np.fft.rfft(x, axis=-1)
    yf = np.fft.rfft(y, axis=-1)
    psd = relative_norm(np.abs(yf) ** 2, np.abs(xf) ** 2)
    covariance = relative_norm(np.cov(y), np.cov(x))
    denominator = max(float(np.linalg.norm(x.mean(axis=-1))), float(np.sqrt(np.mean(x * x))), 1e-12)
    mean = float(np.linalg.norm(y.mean(axis=-1) - x.mean(axis=-1)) / denominator)
    original_cross = np.asarray([np.conj(xf[left]) * xf[right] for left, right in pairs])
    output_cross = np.asarray([np.conj(yf[left]) * yf[right] for left, right in pairs])
    cross = relative_norm(output_cross, original_cross)
    return {"psd": psd, "covariance": covariance, "mean": mean, "cross_spectrum": cross}


class N2CommonPhaseTests(unittest.TestCase):
    def setUp(self) -> None:
        self.sampler = N2CommonPhaseSampler()
        self.fixture = analytic_fixture(513)

    def assert_prefix(self, error: N2CommonPhaseContractError, prefix: str) -> None:
        self.assertTrue(str(error).startswith(prefix + ":"), str(error))

    def test_public_dataclasses_and_exports_are_frozen(self) -> None:
        result = self.sampler.generate_unpadded(self.fixture, ROW_KEY, 1)
        self.assertIsInstance(result, N2TrialSurrogate)
        with self.assertRaises(FrozenInstanceError):
            result.valid_samples = 1
        padded = self.sampler.generate_padded(
            self.fixture.unsqueeze(0), torch.tensor([513]), (ROW_KEY,), 1
        )
        self.assertIsInstance(padded, N2BatchSurrogate)

    def test_exact_seed_byte_law(self) -> None:
        result = self.sampler.generate_unpadded(self.fixture, ROW_KEY, 199)
        expected = hashlib.sha256(
            SEED_PREFIX + struct.pack(">H", 199) + b"\0" + ROW_KEY.encode("ascii")
        ).hexdigest()
        self.assertEqual(result.phase_seed_sha256, expected)

    def test_replay_is_bitwise_and_different_replicates_differ(self) -> None:
        first = self.sampler.generate_unpadded(self.fixture, ROW_KEY, 1)
        replay = self.sampler.generate_unpadded(self.fixture, ROW_KEY, 1)
        second = self.sampler.generate_unpadded(self.fixture, ROW_KEY, 2)
        self.assertTrue(torch.equal(first.values, replay.values))
        self.assertFalse(torch.equal(first.values, second.values))

    def test_input_is_immutable_and_output_contract_is_exact(self) -> None:
        before = self.fixture.clone()
        result = self.sampler.generate_unpadded(self.fixture, ROW_KEY, 2)
        self.assertTrue(torch.equal(self.fixture, before))
        self.assertEqual(result.values.shape, self.fixture.shape)
        self.assertEqual(result.values.dtype, torch.float32)
        self.assertEqual(result.values.device.type, "cpu")
        self.assertTrue(result.values.is_contiguous())
        self.assertEqual(result.valid_samples, 513)

    def test_even_and_odd_preservation_metrics_pass(self) -> None:
        for samples in (500, 501, 513, 2048):
            with self.subTest(samples=samples):
                fixture = analytic_fixture(samples)
                result = self.sampler.generate_unpadded(fixture, f"ZAB\t{samples:06d}\tfixture", 2)
                pairs = tuple((left, right) for left in range(105) for right in range(105)) if samples == 500 else PAIR_PANEL
                metrics = preservation_metrics(fixture, result.values, pairs)
                self.assertTrue(all(np.isfinite(value) and value <= 1e-6 for value in metrics.values()), metrics)

    def test_dc_nyquist_and_common_channel_phase(self) -> None:
        for samples in (500, 501):
            fixture = analytic_fixture(samples)
            result = self.sampler.generate_unpadded(fixture, f"ZAC\t{samples:06d}\tfixture", 1)
            x = np.fft.rfft(fixture.numpy().astype(np.float64), axis=-1)
            y = np.fft.rfft(result.values.numpy().astype(np.float64), axis=-1)
            spectral_scale = max(float(np.linalg.norm(x)), 1e-12)
            self.assertLess(float(np.linalg.norm(y[:, 0] - x[:, 0]) / spectral_scale), 1e-6)
            if samples % 2 == 0:
                self.assertLess(float(np.linalg.norm(y[:, -1] - x[:, -1]) / spectral_scale), 1e-6)
            self.assertLess(relative_norm(np.conj(y[0]) * y[104], np.conj(x[0]) * x[104]), 1e-6)

    def test_all_199_replicates_are_finite_unique_and_replay(self) -> None:
        hashes = []
        fingerprints = []
        for replicate in range(1, 200):
            result = self.sampler.generate_unpadded(self.fixture, ROW_KEY, replicate)
            hashes.append(result.phase_seed_sha256)
            fingerprints.append(hashlib.sha256(result.values.numpy().tobytes()).hexdigest())
            self.assertTrue(bool(torch.isfinite(result.values).all()))
        self.assertEqual(len(set(hashes)), 199)
        self.assertEqual(len(set(fingerprints)), 199)
        replay = self.sampler.generate_unpadded(self.fixture, ROW_KEY, 199)
        self.assertEqual(hashlib.sha256(replay.values.numpy().tobytes()).hexdigest(), fingerprints[-1])

    def test_local_rng_isolation(self) -> None:
        numpy_state = np.random.get_state()
        torch_state = torch.random.get_rng_state().clone()
        self.sampler.generate_unpadded(self.fixture, ROW_KEY, 7)
        after = np.random.get_state()
        self.assertEqual(numpy_state[0], after[0])
        self.assertTrue(np.array_equal(numpy_state[1], after[1]))
        self.assertEqual(numpy_state[2:], after[2:])
        self.assertTrue(torch.equal(torch_state, torch.random.get_rng_state()))

    def test_rejects_rank_channel_dtype_device_contiguous_and_grad(self) -> None:
        cases = (
            self.fixture[0],
            self.fixture[:104],
            self.fixture.to(torch.float64),
            torch.empty((105, 513), dtype=torch.float32, device="meta"),
            self.fixture[:, ::2],
            self.fixture.clone().requires_grad_(True),
        )
        for value in cases:
            with self.subTest(shape=tuple(value.shape), device=value.device):
                with self.assertRaises(N2CommonPhaseContractError) as caught:
                    self.sampler.generate_unpadded(value, ROW_KEY, 1)
                self.assert_prefix(caught.exception, "N2_COMMON_PHASE_INPUT_MISMATCH")

    def test_rejects_nonfinite_and_short_input(self) -> None:
        nonfinite = self.fixture.clone()
        nonfinite[2, 7] = float("nan")
        for value in (nonfinite, analytic_fixture(499)):
            with self.assertRaises(N2CommonPhaseContractError) as caught:
                self.sampler.generate_unpadded(value, ROW_KEY, 1)
            self.assert_prefix(caught.exception, "N2_COMMON_PHASE_INPUT_MISMATCH")

    def test_rejects_noncanonical_row_keys(self) -> None:
        for row_key in (None, "", "ZAB", "ZAB\t17\tx", "ZAB\t000017", "ZÄB\t000017\tx", "ZAB\t000017\tx\ty"):
            with self.subTest(row_key=row_key):
                with self.assertRaises(N2CommonPhaseContractError) as caught:
                    self.sampler.generate_unpadded(self.fixture, row_key, 1)
                self.assert_prefix(caught.exception, "N2_COMMON_PHASE_ROW_KEY_INVALID")

    def test_rejects_invalid_replicates(self) -> None:
        for replicate in (0, 200, True, 1.0, "1"):
            with self.subTest(replicate=replicate):
                with self.assertRaises(N2CommonPhaseContractError) as caught:
                    self.sampler.generate_unpadded(self.fixture, ROW_KEY, replicate)
                self.assert_prefix(caught.exception, "N2_COMMON_PHASE_REPLICATE_INVALID")

    def test_padded_prefix_mask_zero_tail_and_unpadded_parity(self) -> None:
        first = analytic_fixture(513)
        second = analytic_fixture(501)
        values = torch.full((2, 105, 520), float("nan"), dtype=torch.float32)
        values[0, :, :513] = first
        values[1, :, :501] = second
        before = values.clone()
        lengths = torch.tensor([513, 501], dtype=torch.int64)
        keys = ("ZAB\t000001\tfirst", "ZAB\t000002\tsecond")
        result = self.sampler.generate_padded(values, lengths, keys, 3)
        self.assertTrue(torch.allclose(values, before, rtol=0.0, atol=0.0, equal_nan=True))
        for index, (length, key, source) in enumerate(zip(lengths.tolist(), keys, (first, second), strict=True)):
            unpadded = self.sampler.generate_unpadded(source, key, 3)
            self.assertTrue(torch.equal(result.values[index, :, :length], unpadded.values))
            self.assertEqual(torch.count_nonzero(result.values[index, :, length:]).item(), 0)
            self.assertTrue(bool(result.mask[index, :length].all()))
            self.assertFalse(bool(result.mask[index, length:].any()))
        self.assertTrue(torch.equal(result.valid_samples, lengths))

    def test_padded_rejects_invalid_metadata(self) -> None:
        values = torch.zeros((2, 105, 520), dtype=torch.float32)
        valid = torch.tensor([500, 501], dtype=torch.int64)
        keys = ("ZAB\t000001\ta", "ZAB\t000002\tb")
        cases = (
            (valid.to(torch.int32), keys),
            (torch.tensor([499, 501]), keys),
            (torch.tensor([500, 521]), keys),
            (valid, keys[:1]),
            (valid, (keys[0], keys[0])),
            (valid, list(keys)),
        )
        for lengths, row_keys in cases:
            with self.subTest(lengths=lengths, row_keys=row_keys):
                with self.assertRaises(N2CommonPhaseContractError):
                    self.sampler.generate_padded(values, lengths, row_keys, 1)

    def test_independent_channel_phase_mutation_breaks_cross_spectrum(self) -> None:
        x = self.fixture.numpy().astype(np.float64)
        xf = np.fft.rfft(x, axis=-1)
        generator = np.random.Generator(np.random.PCG64(7))
        angles = generator.uniform(-np.pi, np.pi, size=xf.shape)
        angles[:, 0] = 0.0
        mutated = np.fft.irfft(xf * np.exp(1j * angles), n=x.shape[-1], axis=-1).astype(np.float32)
        metrics = preservation_metrics(self.fixture, torch.from_numpy(mutated))
        self.assertGreater(metrics["cross_spectrum"], 1e-6)

    def test_dc_rotation_mutation_breaks_mean(self) -> None:
        x = self.fixture.numpy().astype(np.float64)
        xf = np.fft.rfft(x, axis=-1)
        xf[:, 0] *= np.cos(0.7)
        mutated = np.fft.irfft(xf, n=x.shape[-1], axis=-1).astype(np.float32)
        metrics = preservation_metrics(self.fixture, torch.from_numpy(mutated))
        self.assertGreater(metrics["mean"], 1e-6)

    def test_padding_before_fft_mutation_changes_valid_prefix(self) -> None:
        prefix = analytic_fixture(501)
        padded = torch.zeros((105, 520), dtype=torch.float32)
        padded[:, :501] = prefix
        padded[:, 501:] = 0.25
        correct = self.sampler.generate_unpadded(prefix, ROW_KEY, 5).values
        mutated = self.sampler.generate_unpadded(padded, ROW_KEY, 5).values[:, :501]
        self.assertFalse(torch.equal(correct, mutated))


if __name__ == "__main__":
    unittest.main()
