from __future__ import annotations

import sys
import unittest
from pathlib import Path

import torch


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from rc_hsg.backbones.native_spectral_a1 import (  # noqa: E402
    BANDS_HZ,
    CHANNEL_ORDER_HASH,
    FEATURE_EPSILON,
    PROCESSED_REFERENCE,
    SAMPLING_HZ,
    UNIT_STATUS,
    AInterfaceContractError,
    NativeSpectralA1,
)


METADATA = {
    "channel_order_hash": CHANNEL_ORDER_HASH,
    "sampling_hz": SAMPLING_HZ,
    "unit_status": UNIT_STATUS,
    "processed_reference": PROCESSED_REFERENCE,
}


class NativeSpectralA1Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.model = NativeSpectralA1(20260824).eval()

    def _forward(self, eeg: torch.Tensor, lengths: list[int], **overrides):
        metadata = {**METADATA, **overrides}
        return self.model(eeg, torch.tensor(lengths, dtype=torch.int64), **metadata)

    def _assert_code(self, code: str, eeg: torch.Tensor, lengths, **overrides) -> None:
        with self.assertRaisesRegex(AInterfaceContractError, rf"^{code}:"):
            self._forward(eeg, lengths, **overrides)

    def test_shapes_masks_window_boundaries_and_trailing_discard(self) -> None:
        eeg = torch.randn(3, 105, 800)
        output = self._forward(eeg, [500, 749, 750])
        self.assertEqual(output.window_embeddings.shape, (3, 2, 256))
        self.assertEqual(output.window_mask.dtype, torch.bool)
        self.assertTrue(torch.equal(output.window_mask, torch.tensor([[1, 0], [1, 0], [1, 1]], dtype=torch.bool)))
        self.assertEqual(output.pooled_embedding.shape, (3, 256))
        self.assertTrue(torch.equal(output.window_embeddings[:2, 1], torch.zeros(2, 256)))

    def test_masked_mean_is_exact(self) -> None:
        output = self._forward(torch.randn(2, 105, 1000), [500, 1000])
        expected = (output.window_embeddings * output.window_mask.unsqueeze(-1)).sum(1)
        expected = expected / output.window_mask.sum(1, keepdim=True)
        torch.testing.assert_close(output.pooled_embedding, expected)

    def test_rank_dtype_channel_and_axis_fail_closed(self) -> None:
        self._assert_code("A_INPUT_RANK", torch.zeros(105, 500), [500])
        self._assert_code("A_INPUT_DTYPE", torch.zeros(1, 105, 500, dtype=torch.int64), [500])
        self._assert_code("A_INPUT_CHANNELS", torch.zeros(1, 104, 500), [500])
        self._assert_code("A_INPUT_CHANNELS", torch.zeros(1, 500, 105), [105])

    def test_metadata_mismatches_fail_closed(self) -> None:
        eeg = torch.zeros(1, 105, 500)
        for name, value in (
            ("channel_order_hash", "0" * 64),
            ("sampling_hz", 499),
            ("unit_status", "MICROVOLT"),
            ("processed_reference", "Cz"),
        ):
            self._assert_code("A_METADATA_MISMATCH", eeg, [500], **{name: value})

    def test_valid_samples_and_short_batch_fail_closed(self) -> None:
        eeg = torch.zeros(2, 105, 600)
        self._assert_code("A_SHORT_SEGMENT", eeg, [500, 499])
        with self.assertRaisesRegex(AInterfaceContractError, r"^A_VALID_SAMPLES:"):
            self.model(eeg, torch.tensor([500.0, 500.0]), **METADATA)
        with self.assertRaisesRegex(AInterfaceContractError, r"^A_VALID_SAMPLES:"):
            self.model(eeg, torch.tensor([500]), **METADATA)
        self._assert_code("A_VALID_SAMPLES", eeg, [500, 601])

    def test_nonfinite_valid_slice_fails_but_padding_tail_is_ignored(self) -> None:
        eeg = torch.randn(1, 105, 800)
        invalid = eeg.clone()
        invalid[0, 0, 10] = float("nan")
        self._assert_code("A_NONFINITE", invalid, [750])
        tail_one = eeg.clone()
        tail_two = eeg.clone()
        tail_one[:, :, 750:] = float("nan")
        tail_two[:, :, 750:] = 1.0e20
        first = self._forward(tail_one, [750])
        second = self._forward(tail_two, [750])
        torch.testing.assert_close(first.window_embeddings, second.window_embeddings, rtol=0, atol=0)

    def test_device_mismatch_fails_closed(self) -> None:
        model = NativeSpectralA1(1).to("meta")
        with self.assertRaisesRegex(AInterfaceContractError, r"^A_INPUT_DEVICE:"):
            model(torch.zeros(1, 105, 500), torch.tensor([500]), **METADATA)

    def test_constant_input_is_finite_and_positive_scale_invariant(self) -> None:
        constant = self._forward(torch.full((1, 105, 500), 7.0), [500])
        self.assertTrue(torch.isfinite(constant.window_embeddings).all())
        eeg = torch.randn(1, 105, 750)
        one = self._forward(eeg, [750])
        two = self._forward(eeg * 17.0, [750])
        torch.testing.assert_close(one.window_embeddings, two.window_embeddings, rtol=2e-5, atol=2e-5)

    def test_exact_frequency_bands_hann_fft_epsilon_and_feature_order(self) -> None:
        self.assertEqual(BANDS_HZ, ((1, 4), (4, 8), (8, 10), (10, 13), (13, 20), (20, 30), (30, 45), (55, 75)))
        self.assertEqual([high - low for low, high in BANDS_HZ], [3, 4, 2, 3, 7, 10, 15, 20])
        self.assertEqual(FEATURE_EPSILON, 1.0e-12)
        torch.testing.assert_close(self.model.hann_window, torch.hann_window(500, periodic=False), rtol=0, atol=0)

        time = torch.arange(500, dtype=torch.float32) / 500.0
        eeg = torch.zeros(105, 500)
        eeg[0] = torch.sin(2.0 * torch.pi * 6.0 * time)
        eeg[1] = torch.sin(2.0 * torch.pi * 35.0 * time)
        token = self.model._spectral_tokens(eeg, 500)[0]
        self.assertEqual(token.shape, (840,))
        self.assertEqual(int(token[:8].argmax()), 1)
        self.assertEqual(int(token[8:16].argmax()), 6)

    def test_parameter_count_and_initialization_contract(self) -> None:
        self.assertEqual(sum(p.numel() for p in self.model.parameters() if p.requires_grad), 1_270_528)
        for module in self.model.modules():
            if isinstance(module, torch.nn.LayerNorm):
                self.assertTrue(torch.equal(module.weight, torch.ones_like(module.weight)))
                self.assertTrue(torch.equal(module.bias, torch.zeros_like(module.bias)))
            if isinstance(module, (torch.nn.Linear, torch.nn.MultiheadAttention)):
                bias = module.bias if isinstance(module, torch.nn.Linear) else module.in_proj_bias
                if bias is not None:
                    self.assertTrue(torch.equal(bias, torch.zeros_like(bias)))

    def test_constructor_does_not_pollute_rng_and_seed_is_deterministic(self) -> None:
        torch.manual_seed(77)
        before = torch.random.get_rng_state().clone()
        first = NativeSpectralA1(12).eval()
        after = torch.random.get_rng_state()
        self.assertTrue(torch.equal(before, after))
        second = NativeSpectralA1(12).eval()
        third = NativeSpectralA1(13).eval()
        for key, value in first.state_dict().items():
            self.assertTrue(torch.equal(value, second.state_dict()[key]), key)
        self.assertTrue(any(not torch.equal(a, b) for a, b in zip(first.parameters(), third.parameters())))
        eeg = torch.randn(1, 105, 500)
        lengths = torch.tensor([500])
        one = first(eeg, lengths, **METADATA).window_embeddings
        two = second(eeg, lengths, **METADATA).window_embeddings
        torch.testing.assert_close(one, two, rtol=0, atol=0)

    def test_eval_repeatability_and_finite_backward_gradients(self) -> None:
        eeg = torch.randn(2, 105, 750)
        one = self._forward(eeg, [500, 750])
        two = self._forward(eeg, [500, 750])
        torch.testing.assert_close(one.window_embeddings, two.window_embeddings, rtol=0, atol=0)
        self.model.train()
        output = self._forward(eeg, [500, 750])
        output.pooled_embedding.square().mean().backward()
        gradients = [parameter.grad for parameter in self.model.parameters() if parameter.requires_grad]
        self.assertTrue(all(gradient is not None and torch.isfinite(gradient).all() for gradient in gradients))


if __name__ == "__main__":
    unittest.main()
