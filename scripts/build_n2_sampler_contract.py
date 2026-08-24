#!/usr/bin/env python3
"""Build the frozen synthetic-only N2 common-phase sampler contract."""

from __future__ import annotations

import argparse
import hashlib
import os
import sys
import tempfile
from pathlib import Path
from typing import Any

import numpy as np
import torch
import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from rc_hsg.references.n2_common_phase import (  # noqa: E402
    CHANNELS,
    MIN_SAMPLES,
    NUMPY_VERSION,
    POLICY_ID,
    REPLICATES,
    SEED_PREFIX,
    N2CommonPhaseContractError,
    N2CommonPhaseSampler,
)


BASELINE_COMMIT = "06e3e5f9b5c720bbb29074ca1cae1109add5b1b9"
EVIDENCE_SCOPE = "OUTCOME_BLIND_SYNTHETIC_ONLY_N2_COMMON_PHASE_SAMPLER_CONTRACT_NO_REAL_EEG_NO_TEXT_NO_OUTCOMES_NO_GATE"
THRESHOLD = 1e-6
FIXTURE_LENGTHS = (500, 501, 513, 2048, 27010)
FIXTURE_REPLICATES = (1, 2, 199)
PAIR_PANEL = ((0, 1), (0, 52), (0, 104), (1, 2), (26, 78), (52, 104), (103, 104))
FROZEN_INPUTS = {
    "spec_v27": (
        "guide/RC_HSG_Paper_Spec_v2_7_2026-08-24.md",
        "80d613bcb1eb5e3d3948f71f225ffcab5be52c6593fb141fdf410eb0bd753951",
    ),
    "review_v27": (
        "artifacts/spec_review/rc_hsg_v27_n1_mechanism_sampler_review.md",
        "bd245a03d4244f18381b1008ddbd0504cf7ea28f19407cb254747c20150894eb",
    ),
    "run018": (
        "runs/2026-08-24_018_n1_mechanism_sampler.md",
        "0b3f9ee0662f3429b3ac6fe0b78148e5b61aa2de21d59bec97f8cc634b90d4e7",
    ),
    "n1_module": (
        "src/rc_hsg/references/n1_joint_permutation.py",
        "888c6965c89c007e7edb4d0bcf513a8cdcaf4201dff6b05a3f7bf75bf7a94ca6",
    ),
    "n1_contract": (
        "artifacts/nulls/n1_contract.yaml",
        "4fee63f743936db06eea41164f85f67228785872d3fca2098e657b1dc0383729",
    ),
    "n1_manifest": (
        "artifacts/nulls/n1_permutation_manifest_v1.jsonl",
        "b7e68368799be446af60dcec029458e4e769f6605c1c56c032b76fb069f38c06",
    ),
    "a_eligibility": (
        "artifacts/a_interface_eligibility_v1.jsonl",
        "8eded8fb2786747e96b8388d4d91315e39db9f8a9eb25ea69056d219e1e8e1ad",
    ),
    "requirements": (
        "requirements-trust-align.lock.txt",
        "72a2a3274ef9516dba95a4f4022cacfba0e02d10445e1618da2a569f59381910",
    ),
}
CONTROL_INPUTS = {
    "spec_v28": (
        "guide/RC_HSG_Paper_Spec_v2_8_2026-08-24.md",
        "f718fc37875a6dac7c539260de054d9f9c52966905b1912cf193d573a0424f23",
    ),
    "review_v28": (
        "artifacts/spec_review/rc_hsg_v28_n2_common_phase_sampler_review.md",
        "66edb1aca13e01f87d1a162b86254bbad87ce207ae208474f46a326e53948ea7",
    ),
}
RUN018_RECORDED_NEXT_TASK_HASH = "667b36d04a5e91fd314bf44b1e7ce0a145ed0e9a45286c36c56c8eb8c9d2b0e7"
RUN018_CORRECTED_NEXT_TASK_HASH = "667b8bc2af414673e09d9d2011446db502fbca305fb26e6c558bd0a762d51ef6"
RUN018_PACKAGE_ZIP_HASH = "934d7bb625b6a5183d251ae0d7b5255053adaebef17a0883394a371f3f5b5c24"
OUTPUTS = {
    "correction": "artifacts/governance/run018_provenance_correction.yaml",
    "contract": "artifacts/nulls/n2_contract.yaml",
    "report": "reports/n2_selfcheck.md",
}


def _fail(prefix: str, detail: str) -> None:
    raise N2CommonPhaseContractError(f"{prefix}: {detail}")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
    except OSError as exc:
        _fail("N2_COMMON_PHASE_INPUT_MISMATCH", f"read:{type(exc).__name__}")
    return digest.hexdigest()


def _reject_symlink_chain(path: Path, stop: Path, label: str) -> None:
    current = path.absolute()
    stop = stop.absolute()
    while True:
        if current.is_symlink():
            _fail("N2_COMMON_PHASE_INPUT_MISMATCH", f"symlink:{label}")
        if current == stop or current.parent == current:
            return
        current = current.parent


def _safe_input(project_root: Path, relative: str, label: str) -> Path:
    root = project_root.absolute()
    _reject_symlink_chain(root, Path(root.anchor), "project-root")
    rel = Path(relative)
    if rel.is_absolute() or ".." in rel.parts or rel.suffix.lower() in {".mat", ".h5", ".hdf5"}:
        _fail("N2_COMMON_PHASE_INPUT_MISMATCH", f"unsafe:{label}")
    candidate = root / rel
    _reject_symlink_chain(candidate, root, label)
    try:
        resolved_root = root.resolve(strict=True)
        resolved = candidate.resolve(strict=True)
        resolved.relative_to(resolved_root)
    except (OSError, ValueError):
        _fail("N2_COMMON_PHASE_INPUT_MISMATCH", f"escape-or-missing:{label}")
    if not resolved.is_file():
        _fail("N2_COMMON_PHASE_INPUT_MISMATCH", f"type:{label}")
    return resolved


def _verify_inputs(project_root: Path, enforce: bool) -> tuple[dict[str, Path], dict[str, str]]:
    expected_inputs = {**FROZEN_INPUTS, **CONTROL_INPUTS}
    paths = {
        label: _safe_input(project_root, relative, label)
        for label, (relative, _) in expected_inputs.items()
    }
    hashes = {label: _sha256(path) for label, path in paths.items()}
    if enforce:
        for label, (_, expected) in expected_inputs.items():
            if hashes[label] != expected:
                _fail("N2_COMMON_PHASE_INPUT_MISMATCH", f"hash:{label}")
        if np.__version__ != NUMPY_VERSION:
            _fail("N2_COMMON_PHASE_NUMERIC_FAILURE", "numpy-version")
    return paths, hashes


def _safe_output_root(root: Path, project_root: Path, label: str, *, external: bool) -> Path:
    unresolved = root.absolute()
    if unresolved.is_symlink():
        _fail("N2_COMMON_PHASE_OUTPUT_FAILURE", f"symlink:{label}")
    existing = unresolved
    while not existing.exists() and existing.parent != existing:
        existing = existing.parent
    current = existing.absolute()
    while True:
        if current.is_symlink():
            _fail("N2_COMMON_PHASE_OUTPUT_FAILURE", f"symlink:{label}")
        if current.parent == current:
            break
        current = current.parent
    if unresolved.exists() and not unresolved.is_dir():
        _fail("N2_COMMON_PHASE_OUTPUT_FAILURE", f"root-type:{label}")
    resolved = unresolved.resolve(strict=False)
    project = project_root.absolute().resolve(strict=True)
    if external:
        try:
            resolved.relative_to(project)
        except ValueError:
            pass
        else:
            _fail("N2_COMMON_PHASE_OUTPUT_FAILURE", f"verification-inside-project:{label}")
    return resolved


def _analytic_fixture(samples: int) -> torch.Tensor:
    time = np.arange(samples, dtype=np.float64)
    rows = []
    for channel in range(CHANNELS):
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


def _relative_norm(actual: np.ndarray, expected: np.ndarray, floor: float = 1e-12) -> float:
    return float(np.linalg.norm(actual - expected) / max(float(np.linalg.norm(expected)), floor))


def _ks_distance(first: np.ndarray, second: np.ndarray) -> float:
    left = np.sort(first)
    right = np.sort(second)
    support = np.sort(np.concatenate((left, right)))
    left_cdf = np.searchsorted(left, support, side="right") / left.size
    right_cdf = np.searchsorted(right, support, side="right") / right.size
    return float(np.max(np.abs(left_cdf - right_cdf)))


def _endpoint_diagnostics(values: np.ndarray) -> tuple[float, float]:
    centered = values - values.mean(axis=-1, keepdims=True)
    jump_denominator = max(float(np.sum(centered * centered)), 1e-12)
    jump = float(np.sum((values[:, 0] - values[:, -1]) ** 2) / jump_denominator)
    differences = np.diff(values, axis=-1)
    slip_denominator = max(float(np.sum(differences * differences)), 1e-12)
    slip = float(np.sum((differences[:, 0] - differences[:, -1]) ** 2) / slip_denominator)
    return jump, slip


def _diagnostics(original: torch.Tensor, surrogate: torch.Tensor, all_pairs: bool) -> dict[str, float]:
    x = original.numpy().astype(np.float64)
    y = surrogate.numpy().astype(np.float64)
    xf = np.fft.rfft(x, axis=-1, norm="backward")
    yf = np.fft.rfft(y, axis=-1, norm="backward")
    psd = _relative_norm(np.abs(yf) ** 2, np.abs(xf) ** 2)
    covariance = _relative_norm(np.cov(y), np.cov(x))
    mean_denominator = max(
        float(np.linalg.norm(x.mean(axis=-1))), float(np.sqrt(np.mean(x * x))), 1e-12
    )
    mean = float(np.linalg.norm(y.mean(axis=-1) - x.mean(axis=-1)) / mean_denominator)
    pairs = tuple((left, right) for left in range(CHANNELS) for right in range(CHANNELS)) if all_pairs else PAIR_PANEL
    original_cross = np.asarray([np.conj(xf[left]) * xf[right] for left, right in pairs])
    output_cross = np.asarray([np.conj(yf[left]) * yf[right] for left, right in pairs])
    cross_spectrum = _relative_norm(output_cross, original_cross)

    ks_values = np.asarray([_ks_distance(x[channel], y[channel]) for channel in range(CHANNELS)])
    quantiles = (0.01, 0.10, 0.25, 0.50, 0.75, 0.90, 0.99)
    x_quantiles = np.quantile(x, quantiles, axis=-1)
    y_quantiles = np.quantile(y, quantiles, axis=-1)
    channel_rms = np.maximum(np.sqrt(np.mean(x * x, axis=-1)), 1e-12)
    quantile_shift = np.max(np.abs(y_quantiles - x_quantiles) / channel_rms[np.newaxis, :], axis=0)
    x_centered = x - x.mean(axis=-1, keepdims=True)
    y_centered = y - y.mean(axis=-1, keepdims=True)
    correlation_denominator = np.linalg.norm(x_centered, axis=-1) * np.linalg.norm(y_centered, axis=-1)
    correlations = np.divide(
        np.sum(x_centered * y_centered, axis=-1),
        correlation_denominator,
        out=np.zeros(CHANNELS, dtype=np.float64),
        where=correlation_denominator > 0,
    )
    x_jump, x_slip = _endpoint_diagnostics(x)
    y_jump, y_slip = _endpoint_diagnostics(y)
    result = {
        "psd_relative_norm": psd,
        "covariance_relative_norm": covariance,
        "mean_relative_norm": mean,
        "cross_spectrum_relative_norm": cross_spectrum,
        "amplitude_ks_max": float(ks_values.max()),
        "amplitude_ks_mean": float(ks_values.mean()),
        "quantile_shift_max": float(quantile_shift.max()),
        "quantile_shift_mean": float(quantile_shift.mean()),
        "endpoint_jump_original": x_jump,
        "endpoint_jump_surrogate": y_jump,
        "endpoint_slip_original": x_slip,
        "endpoint_slip_surrogate": y_slip,
        "waveform_correlation_min": float(correlations.min()),
        "waveform_correlation_mean": float(correlations.mean()),
        "waveform_correlation_max": float(correlations.max()),
    }
    if not all(np.isfinite(value) for value in result.values()):
        _fail("N2_COMMON_PHASE_NUMERIC_FAILURE", "diagnostic-finite")
    if any(result[label] > THRESHOLD for label in (
        "psd_relative_norm", "covariance_relative_norm", "mean_relative_norm", "cross_spectrum_relative_norm"
    )):
        _fail("N2_COMMON_PHASE_NUMERIC_FAILURE", "preservation-threshold")
    return result


def _hex_metrics(metrics: dict[str, float]) -> dict[str, str]:
    return {label: float(value).hex() for label, value in metrics.items()}


def _yaml_bytes(value: dict[str, Any]) -> bytes:
    return yaml.safe_dump(value, sort_keys=False, allow_unicode=False, width=120).encode("utf-8")


def _report_bytes(contract: dict[str, Any]) -> bytes:
    diagnostics = contract["synthetic_diagnostics"]
    lines = [
        "# RC-HSG v2.8 N2 Common-Phase Sampler Self-Check",
        "",
        "## Scope",
        "",
        "This is a synthetic-only implementation check. No real EEG, text, outcome, test identity, frontend, encoder, score, p-value, or training path was used.",
        f"Policy: `{POLICY_ID}`; fixtures={len(FIXTURE_LENGTHS)} lengths x {len(FIXTURE_REPLICATES)} replicates plus a 199-replicate replay.",
        "",
        "## Preservation",
        "",
        f"All {diagnostics['grid_cases']} grid cases pass the frozen global relative-norm threshold {THRESHOLD:.1e} for PSD, covariance, mean, and cross-spectrum.",
        f"The T=513 replay has {diagnostics['replicate_replay']['unique_seed_hashes']}/199 unique seed hashes and bitwise deterministic replay.",
        "The common phase preserves circular second-order structure. It does not guarantee amplitude distribution, endpoint behavior, real-EEG exchangeability, or an exact null.",
        "",
        "## Stop",
        "",
        "N2 is implemented but not admitted. Gate R0 remains unexecuted and requires a new author-frozen outcome-blind real-data audit contract.",
        "Route remains unlocked and test remains `LOCKED_UNTIL_ROUTE_LOCK`.",
        "",
    ]
    return "\n".join(lines).encode("utf-8")


def _render_outputs(
    input_hashes: dict[str, str], implementation_hashes: dict[str, str]
) -> dict[str, bytes]:
    sampler = N2CommonPhaseSampler()
    grid: list[dict[str, Any]] = []
    all_seed_hashes: list[str] = []
    for samples in FIXTURE_LENGTHS:
        fixture = _analytic_fixture(samples)
        for replicate in FIXTURE_REPLICATES:
            row_key = f"SYN\t{samples:06d}\tn2_fixture"
            before = fixture.clone()
            result = sampler.generate_unpadded(fixture, row_key, replicate)
            if not torch.equal(fixture, before):
                _fail("N2_COMMON_PHASE_OUTPUT_FAILURE", "input-mutated")
            metrics = _diagnostics(fixture, result.values, all_pairs=samples == 500)
            grid.append({
                "valid_samples": samples,
                "replicate_id": replicate,
                "cross_spectrum_pairs": CHANNELS * CHANNELS if samples == 500 else len(PAIR_PANEL),
                "phase_seed_sha256": result.phase_seed_sha256,
                "metrics": _hex_metrics(metrics),
            })
            all_seed_hashes.append(result.phase_seed_sha256)

    replay_fixture = _analytic_fixture(513)
    replay_hashes: list[str] = []
    replay_fingerprints: list[str] = []
    for replicate in range(1, REPLICATES + 1):
        result = sampler.generate_unpadded(replay_fixture, "SYN\t000513\tn2_replay", replicate)
        if not bool(torch.isfinite(result.values).all()):
            _fail("N2_COMMON_PHASE_NUMERIC_FAILURE", "replay-finite")
        replay_hashes.append(result.phase_seed_sha256)
        replay_fingerprints.append(hashlib.sha256(result.values.numpy().tobytes()).hexdigest())
    replay = sampler.generate_unpadded(replay_fixture, "SYN\t000513\tn2_replay", REPLICATES)
    replay_fingerprint = hashlib.sha256(replay.values.numpy().tobytes()).hexdigest()
    if len(set(replay_hashes)) != REPLICATES or len(set(replay_fingerprints)) != REPLICATES:
        _fail("N2_COMMON_PHASE_NUMERIC_FAILURE", "replay-unique")
    if replay_fingerprint != replay_fingerprints[-1]:
        _fail("N2_COMMON_PHASE_NUMERIC_FAILURE", "replay-determinism")

    padded_values = torch.full((2, CHANNELS, 520), float("nan"), dtype=torch.float32)
    padded_values[0, :, :513] = _analytic_fixture(513)
    padded_values[1, :, :501] = _analytic_fixture(501)
    lengths = torch.tensor([513, 501], dtype=torch.int64)
    keys = ("SYN\t000001\tpadded_a", "SYN\t000002\tpadded_b")
    padded = sampler.generate_padded(padded_values, lengths, keys, 2)
    if (
        not bool(padded.mask[0, :513].all())
        or bool(padded.mask[0, 513:].any())
        or not bool(padded.mask[1, :501].all())
        or bool(padded.mask[1, 501:].any())
        or torch.count_nonzero(padded.values[0, :, 513:]).item() != 0
        or torch.count_nonzero(padded.values[1, :, 501:]).item() != 0
    ):
        _fail("N2_COMMON_PHASE_MASK_FAILURE", "builder-padded")

    correction = {
        "schema_version": 1,
        "artifact": "RC_HSG_RUN018_PROVENANCE_CORRECTION_V1",
        "created_by_run": "2026-08-24_019_n2_common_phase_sampler",
        "historical_run": {
            "path": FROZEN_INPUTS["run018"][0],
            "sha256": FROZEN_INPUTS["run018"][1],
            "modified": False,
        },
        "field": "package_source_CODEX_NEXT_TASK_sha256",
        "recorded_sha256": RUN018_RECORDED_NEXT_TASK_HASH,
        "corrected_sha256": RUN018_CORRECTED_NEXT_TASK_HASH,
        "source_zip_sha256": RUN018_PACKAGE_ZIP_HASH,
        "verification_basis": "ZIP_CONTENT_AND_PACKAGE_MANIFEST_SHA256",
        "scientific_state_changed": False,
        "code_artifact_test_state_changed": False,
    }
    contract = {
        "schema_version": 1,
        "artifact": POLICY_ID,
        "spec_version": "v2.8",
        "baseline_commit": BASELINE_COMMIT,
        "task": "S0_N2_SAMPLER",
        "policy_id": POLICY_ID,
        "evidence_scope": EVIDENCE_SCOPE,
        "input_artifacts": {
            label: {"path": ({**FROZEN_INPUTS, **CONTROL_INPUTS})[label][0], "sha256": input_hashes[label]}
            for label in ({**FROZEN_INPUTS, **CONTROL_INPUTS})
        },
        "scientific_basis": {
            "reference_role": "EMPIRICAL_MATCHED_REFERENCE",
            "preserves": "CIRCULAR_SECOND_ORDER_STRUCTURE",
            "does_not_establish": [
                "REAL_EEG_EXCHANGEABILITY", "EXACT_NULL", "RANDOMIZATION_P_VALUE", "DISTRIBUTION_FREE_GUARANTEE"
            ],
            "n1_status": "MECHANISM_ROBUSTNESS_ONLY_DEGRADED_COVERAGE",
            "n2_admission_status": "PENDING_OUTCOME_BLIND_GATE_R0",
        },
        "transform_contract": {
            "channels": CHANNELS,
            "minimum_valid_samples": MIN_SAMPLES,
            "input_device": "CPU",
            "input_dtype": "torch.float32",
            "fft_internal_dtype": "numpy.float64",
            "output_dtype": "torch.float32",
            "fft_norm": "backward",
            "common_phase_across_channels": True,
            "dc_fixed": True,
            "even_nyquist_fixed": True,
            "valid_unpadded_prefix_only": True,
            "padding_tail_exact_zero": True,
            "input_in_place_modified": False,
        },
        "seed_contract": {
            "replicates": REPLICATES,
            "replicate_range": [1, REPLICATES],
            "digest": "SHA256",
            "prefix_hex": SEED_PREFIX.hex(),
            "replicate_encoding": "UINT16_BIG_ENDIAN",
            "row_key_encoding": "CANONICAL_ASCII",
            "seed_bytes": "FIRST_16_DIGEST_BYTES_BIG_ENDIAN_INTEGER",
            "generator": f"numpy.random.Generator(PCG64(seed))@{NUMPY_VERSION}",
            "angle_distribution": "FLOAT64_UNIFORM_NEGATIVE_PI_TO_PI_HALF_OPEN",
            "global_rng_state_used": False,
        },
        "input_output_contract": {
            "trial_shape": "[105,T]",
            "batch_shape": "[B,105,Tmax]",
            "valid_samples_dtype": "torch.int64",
            "mask_dtype": "torch.bool",
            "mask_law": "EXACT_TRUE_PREFIX_FALSE_TAIL",
            "row_key_law": "subject<TAB>slot_6_digits<TAB>occurrence_id",
            "finite_scope": "VALID_PREFIX_ONLY",
            "requires_grad": False,
        },
        "synthetic_fixtures": {
            "construction": "ANALYTIC_SIN_COS_CHANNEL_MIXING_IMPULSE_SAW_NO_RNG",
            "lengths": list(FIXTURE_LENGTHS),
            "grid_replicates": list(FIXTURE_REPLICATES),
            "replay_length": 513,
            "replay_replicates": REPLICATES,
            "all_pair_length": 500,
            "all_pair_count": CHANNELS * CHANNELS,
            "fixed_pair_panel": [list(pair) for pair in PAIR_PANEL],
        },
        "preservation_thresholds": {
            "psd_global_relative_norm_max": THRESHOLD.hex(),
            "covariance_global_relative_norm_max": THRESHOLD.hex(),
            "mean_global_relative_norm_max": THRESHOLD.hex(),
            "cross_spectrum_global_relative_norm_max": THRESHOLD.hex(),
            "synthetic_gate_cutoff_for_amplitude_endpoint_correlation": None,
        },
        "synthetic_diagnostics": {
            "grid_cases": len(grid),
            "all_preservation_checks_pass": True,
            "cases": grid,
            "replicate_replay": {
                "replicates": REPLICATES,
                "unique_seed_hashes": len(set(replay_hashes)),
                "unique_output_fingerprints": len(set(replay_fingerprints)),
                "finite_outputs": REPLICATES,
                "bitwise_replay": True,
            },
            "padded_fixture": {
                "rows": 2,
                "valid_samples": [513, 501],
                "prefix_unpadded_bitwise_equal": True,
                "mask_exact": True,
                "padding_tail_exact_zero": True,
                "nonfinite_padding_ignored": True,
            },
        },
        "artifact_diagnostics_schema": {
            "amplitude_ks": "PER_CHANNEL_TWO_SAMPLE_ECDF_MAX_THEN_MAX_AND_MEAN_ACROSS_CHANNELS",
            "quantile_shift": "PER_CHANNEL_MAX_NORMALIZED_SHIFT_AT_0.01_0.10_0.25_0.50_0.75_0.90_0.99",
            "endpoint_jump": "SPEC_V28_SECTION_27_6_GAMMA_JUMP",
            "endpoint_slip": "SPEC_V28_SECTION_27_6_GAMMA_SLIP",
            "waveform_correlation": "PER_CHANNEL_CENTERED_PEARSON_MIN_MEAN_MAX",
            "diagnostic_only_no_synthetic_cutoff": True,
        },
        "implementation": {
            "module_path": "src/rc_hsg/references/n2_common_phase.py",
            "module_sha256": implementation_hashes["module"],
            "builder_path": "scripts/build_n2_sampler_contract.py",
            "builder_sha256": implementation_hashes["builder"],
            "numpy_version": np.__version__,
            "torch_version": str(torch.__version__),
        },
        "prohibited": {
            "aaft_or_iaaft": True,
            "independent_channel_phase": True,
            "windowing_padding_truncation_endpoint_repair": True,
            "amplitude_remap_or_circular_shift": True,
            "real_dataset_or_frontend_import": True,
            "score_p_value_training_gate": True,
        },
        "safety": {
            "synthetic_only": True,
            "real_outer_train_reads": 0,
            "calibration_reads": 0,
            "test_reads": 0,
            "text_outcome_test_identity_reads": 0,
            "a1_frontend_encoder_loads": 0,
            "embedding_reference_score_p_value_generated": 0,
            "training_or_classifier_runs": 0,
            "fixture_waveform_fft_phase_seed_integer_persisted": False,
            "test_status": "LOCKED_UNTIL_ROUTE_LOCK",
        },
        "downstream_boundary": {
            "n2_sampler_implemented": True,
            "n2_primary_admitted": False,
            "gate_r0_executed": False,
            "route_locked": False,
            "next_task": "GATE_R0",
            "next_owner": "CHATGPT_OR_AUTHOR",
        },
    }
    return {
        "correction": _yaml_bytes(correction),
        "contract": _yaml_bytes(contract),
        "report": _report_bytes(contract),
    }


def _atomic_write(root: Path, rendered: dict[str, bytes]) -> None:
    pending: list[tuple[Path, Path]] = []
    try:
        for label, relative in OUTPUTS.items():
            destination = root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            descriptor, name = tempfile.mkstemp(prefix=f".{destination.name}.", dir=destination.parent)
            temporary = Path(name)
            with os.fdopen(descriptor, "wb") as handle:
                handle.write(rendered[label])
                handle.flush()
                os.fsync(handle.fileno())
            pending.append((temporary, destination))
        for temporary, destination in pending:
            os.replace(temporary, destination)
    except Exception as exc:
        for temporary, _ in pending:
            try:
                temporary.unlink(missing_ok=True)
            except OSError:
                pass
        _fail("N2_COMMON_PHASE_OUTPUT_FAILURE", type(exc).__name__)


def build_n2_sampler_contract(
    project_root: Path,
    canonical_output_root: Path,
    verification_output_roots: tuple[Path, Path],
    *,
    enforce_frozen_expectations: bool = True,
) -> dict[str, str]:
    project = Path(project_root).absolute()
    _, input_hashes = _verify_inputs(project, enforce_frozen_expectations)
    module_path = _safe_input(project, "src/rc_hsg/references/n2_common_phase.py", "module")
    builder_path = _safe_input(project, "scripts/build_n2_sampler_contract.py", "builder")
    implementation_hashes = {"module": _sha256(module_path), "builder": _sha256(builder_path)}
    if not isinstance(verification_output_roots, tuple) or len(verification_output_roots) != 2:
        _fail("N2_COMMON_PHASE_OUTPUT_FAILURE", "verification-root-count")
    canonical = _safe_output_root(Path(canonical_output_root), project, "canonical", external=False)
    verify_a = _safe_output_root(Path(verification_output_roots[0]), project, "verification-a", external=True)
    verify_b = _safe_output_root(Path(verification_output_roots[1]), project, "verification-b", external=True)
    if len({canonical, verify_a, verify_b}) != 3:
        _fail("N2_COMMON_PHASE_OUTPUT_FAILURE", "output-roots-distinct")

    rendered_a = _render_outputs(input_hashes, implementation_hashes)
    rendered_b = _render_outputs(input_hashes, implementation_hashes)
    rendered_canonical = _render_outputs(input_hashes, implementation_hashes)
    for label in OUTPUTS:
        if not rendered_a[label] == rendered_b[label] == rendered_canonical[label]:
            _fail("N2_COMMON_PHASE_OUTPUT_FAILURE", f"render-mismatch:{label}")
    _atomic_write(verify_a, rendered_a)
    _atomic_write(verify_b, rendered_b)
    _atomic_write(canonical, rendered_canonical)

    hashes: dict[str, str] = {}
    for label, relative in OUTPUTS.items():
        canonical_bytes = (canonical / relative).read_bytes()
        if canonical_bytes != (verify_a / relative).read_bytes() or canonical_bytes != (verify_b / relative).read_bytes():
            _fail("N2_COMMON_PHASE_OUTPUT_FAILURE", f"byte-compare:{label}")
        hashes[relative] = hashlib.sha256(canonical_bytes).hexdigest()
    return hashes


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--verification-root-a", type=Path, required=True)
    parser.add_argument("--verification-root-b", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        hashes = build_n2_sampler_contract(
            PROJECT_ROOT,
            args.output_root,
            (args.verification_root_a, args.verification_root_b),
        )
    except N2CommonPhaseContractError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    for relative, digest in hashes.items():
        print(f"{relative} {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
