#!/usr/bin/env python3
"""Build the frozen metadata-only N1 mechanism sampler contract."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from rc_hsg.references.n1_joint_permutation import (  # noqa: E402
    EXPECTED_EVALUABLE_BLOCKS,
    EXPECTED_EVALUABLE_ROWS,
    EXPECTED_EXCLUSIONS,
    EXPECTED_ROWS,
    N1JointPermutationSampler,
    N1SamplerContractError,
    POLICY_ID,
    REPLICATES,
)


BASELINE_COMMIT = "082ed4f72f1b8bbc18096a5f0caea2075b2783c4"
EVIDENCE_SCOPE = "OUTCOME_BLIND_N1_MECHANISM_ONLY_INDEX_SAMPLER_FROM_FROZEN_RUN017_ASSIGNMENT_NO_EEG_READ_NO_REFERENCE_SCORE_NO_PVALUES"
EXPECTED_FIXED_TOTAL = 35529
EXPECTED_FIXED_MIN = 145
EXPECTED_FIXED_MAX = 214
FIXED_INPUTS = {
    "spec_v26": (
        "guide/RC_HSG_Paper_Spec_v2_6_2026-08-24.md",
        "174f0ee08870cc045a75336d3fc7138c97a99e78e5adfb109aed74b5c5144aaa",
    ),
    "review_v26": (
        "artifacts/spec_review/rc_hsg_v26_n1_block_feasibility_review.md",
        "b44e0a97c57d8e51e3e8365c56781c88b37328acc28d21f40f070e876d421e87",
    ),
    "assignment": (
        "artifacts/nulls/n1_block_assignment_v1.jsonl",
        "d0acc5e5fe78bc36a69cb04b6f605983c675e49a764538ae1665f86a28acee04",
    ),
    "feasibility": (
        "artifacts/nulls/n1_block_feasibility.yaml",
        "90a6178100f507299e12223d15291699aad84e4b58bb52e29843dbf99ee6f771",
    ),
    "feasibility_report": (
        "reports/n1_block_feasibility.md",
        "5bf77b8282d0938d59104b5e4e615c30c3b4fbdc089dab2ccc1bbd019da14098",
    ),
    "feasibility_code": (
        "scripts/audit_n1_block_feasibility.py",
        "beb4c739c05a225b5fe41e796a6d7a7c0fa60239d6b14dab51f28ba6d83d75ad",
    ),
    "run017": (
        "runs/2026-08-24_017_n1_block_feasibility.md",
        "bf61b04a19f7586d44aec7d6f5b29b38666cce90225964c8f8af250766370eab",
    ),
    "split": (
        "artifacts/split_regimeI.json",
        "e2c065e5b395053cd655670fede8a2b117f6eb9821af884ca31c6fed3842fbab",
    ),
    "admission_ledger": (
        "artifacts/a1_outer_train_admission_v1.jsonl",
        "b3c1b4e11855ef4c51c5bd0c2c0009f8a24e390c511d97118c48082fc7febfd5",
    ),
    "spec_v27": (
        "guide/RC_HSG_Paper_Spec_v2_7_2026-08-24.md",
        "80d613bcb1eb5e3d3948f71f225ffcab5be52c6593fb141fdf410eb0bd753951",
    ),
    "review_v27": (
        "artifacts/spec_review/rc_hsg_v27_n1_mechanism_sampler_review.md",
        "bd245a03d4244f18381b1008ddbd0504cf7ea28f19407cb254747c20150894eb",
    ),
}
OUTPUTS = {
    "contract": "artifacts/nulls/n1_contract.yaml",
    "manifest": "artifacts/nulls/n1_permutation_manifest_v1.jsonl",
    "report": "reports/n1_selfcheck.md",
}
MANIFEST_FIELDS = (
    "replicate_id", "policy_id", "evaluable_rows", "evaluable_blocks", "fixed_points",
    "fixed_point_rate", "joint_mapping_sha256",
)


def _fail(code: str, detail: str) -> None:
    raise N1SamplerContractError(f"{code}: {detail}")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
    except OSError as exc:
        _fail("N1_SAMPLER_INPUT_MISMATCH", f"read:{type(exc).__name__}")
    return digest.hexdigest()


def _reject_symlink_chain(path: Path, stop: Path, code: str, label: str) -> None:
    current = path.absolute()
    stop = stop.absolute()
    while True:
        if current.is_symlink():
            _fail(code, f"symlink:{label}")
        if current == stop or current.parent == current:
            return
        current = current.parent


def _safe_input(project_root: Path, relative: str, label: str) -> Path:
    root = project_root.absolute()
    _reject_symlink_chain(root, Path(root.anchor), "N1_SAMPLER_INPUT_MISMATCH", "project-root")
    rel = Path(relative)
    if rel.is_absolute() or ".." in rel.parts or rel.suffix.lower() in {".mat", ".h5", ".hdf5"}:
        _fail("N1_SAMPLER_INPUT_MISMATCH", f"unsafe:{label}")
    candidate = root / rel
    _reject_symlink_chain(candidate, root, "N1_SAMPLER_INPUT_MISMATCH", label)
    try:
        resolved_root = root.resolve(strict=True)
        resolved = candidate.resolve(strict=True)
        resolved.relative_to(resolved_root)
    except (OSError, ValueError):
        _fail("N1_SAMPLER_INPUT_MISMATCH", f"escape-or-missing:{label}")
    if not resolved.is_file():
        _fail("N1_SAMPLER_INPUT_MISMATCH", f"type:{label}")
    return resolved


def _verify_inputs(project_root: Path, enforce: bool) -> tuple[dict[str, Path], dict[str, str]]:
    paths = {
        label: _safe_input(project_root, relative, label)
        for label, (relative, _) in FIXED_INPUTS.items()
    }
    hashes = {label: _sha256(path) for label, path in paths.items()}
    if enforce:
        for label, (_, expected) in FIXED_INPUTS.items():
            if hashes[label] != expected:
                _fail("N1_SAMPLER_INPUT_MISMATCH", f"hash:{label}")
    return paths, hashes


def _safe_output_root(
    root: Path,
    project_root: Path,
    label: str,
    *,
    external: bool,
) -> Path:
    unresolved = root.absolute()
    if unresolved.is_symlink():
        _fail("N1_SAMPLER_OUTPUT_FAILURE", f"symlink:{label}")
    existing = unresolved
    while not existing.exists() and existing.parent != existing:
        existing = existing.parent
    _reject_symlink_chain(existing, Path(existing.anchor), "N1_SAMPLER_OUTPUT_FAILURE", label)
    if unresolved.exists() and not unresolved.is_dir():
        _fail("N1_SAMPLER_OUTPUT_FAILURE", f"root-type:{label}")
    resolved = unresolved.resolve(strict=False)
    resolved_project = project_root.absolute().resolve(strict=True)
    if external:
        try:
            resolved.relative_to(resolved_project)
        except ValueError:
            pass
        else:
            _fail("N1_SAMPLER_OUTPUT_FAILURE", f"verification-inside-project:{label}")
    return resolved


def _load_feasibility(path: Path) -> list[dict[str, Any]]:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        _fail("N1_SAMPLER_INPUT_MISMATCH", f"feasibility-yaml:{type(exc).__name__}")
    try:
        replicates = value["permutation_probe"]["replicates"]
    except (TypeError, KeyError):
        _fail("N1_SAMPLER_INPUT_MISMATCH", "feasibility-schema")
    if not isinstance(replicates, list) or len(replicates) != REPLICATES:
        _fail("N1_SAMPLER_INPUT_MISMATCH", "feasibility-replicates")
    expected: list[dict[str, Any]] = []
    for index, item in enumerate(replicates, start=1):
        if (
            not isinstance(item, dict)
            or tuple(item) != (
                "replicate_id", "joint_mapping_sha256", "evaluable_rows", "fixed_points"
            )
            or item.get("replicate_id") != index
            or item.get("evaluable_rows") != EXPECTED_EVALUABLE_ROWS
            or not isinstance(item.get("joint_mapping_sha256"), str)
            or len(item["joint_mapping_sha256"]) != 64
            or not isinstance(item.get("fixed_points"), int)
            or isinstance(item.get("fixed_points"), bool)
        ):
            _fail("N1_SAMPLER_INPUT_MISMATCH", f"feasibility-replicate:{index}")
        expected.append(item)
    return expected


def _yaml_bytes(value: dict[str, Any]) -> bytes:
    return yaml.safe_dump(
        value, sort_keys=False, allow_unicode=False, width=120
    ).encode("utf-8")


def _manifest_bytes(rows: list[dict[str, Any]]) -> bytes:
    return "".join(
        json.dumps(row, ensure_ascii=True, separators=(",", ":")) + "\n" for row in rows
    ).encode("utf-8")


def _report_bytes(contract: dict[str, Any]) -> bytes:
    parity = contract["parity"]
    scope = contract["assignment_scope"]
    lines = [
        "# RC-HSG v2.7 N1 Mechanism Sampler Self-Check",
        "",
        "## Frozen scope",
        "",
        f"The committed assignment contains {scope['outer_train_rows']:,} rows: "
        f"{scope['evaluable_rows']:,} evaluable rows in {scope['evaluable_blocks']} blocks and "
        f"{scope['excluded_rows']} canonical exclusions.",
        "N1 remains a mechanism/robustness family because run 017 froze DEGRADED_COVERAGE; it is not a primary fallback.",
        "",
        "## Permutation parity",
        "",
        f"All {parity['replicates']} metadata-only joint permutations match the run-017 hashes and fixed-point counts.",
        f"The hashes are {parity['unique_joint_mapping_hashes']}/{parity['replicates']} unique; fixed points total "
        f"{parity['fixed_points_total']:,} with range {parity['fixed_points_min']}..{parity['fixed_points_max']}.",
        "Fixed points are retained. Adjacent-block borrowing, cross-scope mapping, RNG, and persisted mapping relations are absent.",
        "",
        "## Selection-aware boundary",
        "",
        "Real and pseudo-real sources use the same complete select-then-score callback in canonical row order.",
        "Candidate selection, the L1-L2-L3 parent-consistent path, and scoring must be recomputed inside every callback invocation.",
        "This run creates no semantic candidates, reference scores, donor values, or paper p-values.",
        "",
        "## Safety and stop",
        "",
        "The build reads committed metadata only. EEG, short, calibration, test, text, outcome, frontend, token, proxy, embedding, and waveform reads are zero.",
        "No N2 implementation or Gate is executed. The next task is `S0_N2_SAMPLER`, owner `CHATGPT_OR_AUTHOR`.",
        "",
    ]
    return "\n".join(lines).encode("utf-8")


def _render_outputs(
    project_root: Path,
    input_paths: dict[str, Path],
    input_hashes: dict[str, str],
    implementation_hashes: dict[str, str],
) -> dict[str, bytes]:
    sampler = N1JointPermutationSampler.from_frozen_assignment(project_root)
    expected = _load_feasibility(input_paths["feasibility"])
    manifest_rows: list[dict[str, Any]] = []
    hashes: list[str] = []
    fixed_points: list[int] = []
    for replicate_id, oracle in enumerate(expected, start=1):
        batch = sampler.build(replicate_id)
        if (
            batch.joint_mapping_sha256 != oracle["joint_mapping_sha256"]
            or batch.fixed_points != oracle["fixed_points"]
            or len(batch.pairs) != EXPECTED_EVALUABLE_ROWS
            or len(batch.excluded_row_keys) != EXPECTED_EXCLUSIONS
            or len({pair.block_id for pair in batch.pairs}) != EXPECTED_EVALUABLE_BLOCKS
        ):
            _fail("N1_SAMPLER_SCOPE_MISMATCH", f"parity:{replicate_id}")
        row = {
            "replicate_id": replicate_id,
            "policy_id": POLICY_ID,
            "evaluable_rows": EXPECTED_EVALUABLE_ROWS,
            "evaluable_blocks": EXPECTED_EVALUABLE_BLOCKS,
            "fixed_points": batch.fixed_points,
            "fixed_point_rate": format(batch.fixed_points / EXPECTED_EVALUABLE_ROWS, ".12f"),
            "joint_mapping_sha256": batch.joint_mapping_sha256,
        }
        if tuple(row) != MANIFEST_FIELDS:
            _fail("N1_SAMPLER_OUTPUT_FAILURE", "manifest-fields")
        manifest_rows.append(row)
        hashes.append(batch.joint_mapping_sha256)
        fixed_points.append(batch.fixed_points)

    if (
        len(set(hashes)) != REPLICATES
        or sum(fixed_points) != EXPECTED_FIXED_TOTAL
        or min(fixed_points) != EXPECTED_FIXED_MIN
        or max(fixed_points) != EXPECTED_FIXED_MAX
    ):
        _fail("N1_SAMPLER_SCOPE_MISMATCH", "aggregate-parity")

    contract = {
        "schema_version": 1,
        "artifact": "RC_HSG_N1_JOINT_PERMUTATION_SAMPLER_V1",
        "spec_version": "v2.7",
        "baseline_commit": BASELINE_COMMIT,
        "task": "S0_N1_SAMPLER",
        "policy_id": POLICY_ID,
        "evidence_scope": EVIDENCE_SCOPE,
        "input_artifacts": {
            label: {"path": FIXED_INPUTS[label][0], "sha256": input_hashes[label]}
            for label in FIXED_INPUTS
        },
        "assignment_scope": {
            "outer_train_rows": EXPECTED_ROWS,
            "evaluable_rows": EXPECTED_EVALUABLE_ROWS,
            "evaluable_blocks": EXPECTED_EVALUABLE_BLOCKS,
            "excluded_rows": EXPECTED_EXCLUSIONS,
            "exclusion_counts": {
                "short_forced_l0": 44,
                "power_edge_unavailable": 4,
                "singleton": 12,
            },
        },
        "permutation_contract": {
            "replicates": REPLICATES,
            "algorithm": "SHA256_HASH_SORT_WITHIN_BLOCK_BIJECTION",
            "replicate_range": [1, REPLICATES],
            "fixed_points_retained": True,
            "adjacent_block_borrowing": False,
            "cross_scope_mapping": False,
            "rng_used": False,
            "python_hash_used": False,
        },
        "parity": {
            "replicates": REPLICATES,
            "exact_hash_matches": REPLICATES,
            "exact_fixed_point_matches": REPLICATES,
            "unique_joint_mapping_hashes": len(set(hashes)),
            "fixed_points_total": sum(fixed_points),
            "fixed_points_min": min(fixed_points),
            "fixed_points_max": max(fixed_points),
            "bijection_violations": 0,
            "cross_block_violations": 0,
        },
        "selection_aware_boundary": {
            "value_key_scope": "EXACT_3481_EVALUABLE_ROWS",
            "canonical_callback_calls_per_observation": EXPECTED_EVALUABLE_ROWS,
            "same_select_then_score_callback": True,
            "candidate_selection_recomputed": True,
            "parent_consistent_path_recomputed": True,
            "score_recomputed": True,
            "candidate_specific_shortcut": False,
            "paper_p_value_computed": False,
        },
        "implementation": {
            "module_path": "src/rc_hsg/references/n1_joint_permutation.py",
            "module_sha256": implementation_hashes["module"],
            "builder_path": "scripts/build_n1_sampler_contract.py",
            "builder_sha256": implementation_hashes["builder"],
            "feasibility_script_imported": False,
            "frontend_or_a1_imported": False,
        },
        "outputs": [OUTPUTS[label] for label in OUTPUTS],
        "safety": {
            "metadata_only": True,
            "production_eeg_reads": 0,
            "short_array_reads": 0,
            "calibration_array_reads": 0,
            "test_array_reads": 0,
            "text_or_outcome_reads": 0,
            "frontend_or_tokenizer_loads": 0,
            "proxy_token_embedding_waveform_reads": 0,
            "mapping_relations_persisted": False,
            "semantic_candidate_or_reference_score_generated": False,
            "donor_value_generated": False,
            "paper_p_value_computed": False,
            "test_status": "LOCKED_UNTIL_ROUTE_LOCK",
        },
        "downstream_boundary": {
            "n1_mechanism_sampler_implemented": True,
            "n1_primary_admitted": False,
            "n2_sampler_implemented": False,
            "gate_r0_executed": False,
            "route_locked": False,
            "next_task": "S0_N2_SAMPLER",
            "next_owner": "CHATGPT_OR_AUTHOR",
        },
    }
    rendered = {
        "contract": _yaml_bytes(contract),
        "manifest": _manifest_bytes(manifest_rows),
        "report": _report_bytes(contract),
    }
    return rendered


def _atomic_write(root: Path, rendered: dict[str, bytes]) -> None:
    pending: list[tuple[Path, Path]] = []
    try:
        for label, relative in OUTPUTS.items():
            destination = root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            descriptor, name = tempfile.mkstemp(
                prefix=f".{destination.name}.", dir=destination.parent
            )
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
        _fail("N1_SAMPLER_OUTPUT_FAILURE", type(exc).__name__)


def build_n1_sampler_contract(
    project_root: Path,
    canonical_output_root: Path,
    verification_output_roots: tuple[Path, Path],
    *,
    enforce_frozen_expectations: bool = True,
) -> dict[str, str]:
    project = Path(project_root).absolute()
    input_paths, input_hashes = _verify_inputs(project, enforce_frozen_expectations)
    module_path = _safe_input(
        project, "src/rc_hsg/references/n1_joint_permutation.py", "module"
    )
    builder_path = _safe_input(project, "scripts/build_n1_sampler_contract.py", "builder")
    implementation_hashes = {
        "module": _sha256(module_path),
        "builder": _sha256(builder_path),
    }

    if not isinstance(verification_output_roots, tuple) or len(verification_output_roots) != 2:
        _fail("N1_SAMPLER_OUTPUT_FAILURE", "verification-root-count")
    canonical = _safe_output_root(
        Path(canonical_output_root), project, "canonical", external=False
    )
    verify_a = _safe_output_root(
        Path(verification_output_roots[0]), project, "verification-a", external=True
    )
    verify_b = _safe_output_root(
        Path(verification_output_roots[1]), project, "verification-b", external=True
    )
    if len({canonical, verify_a, verify_b}) != 3:
        _fail("N1_SAMPLER_OUTPUT_FAILURE", "output-roots-distinct")

    rendered_a = _render_outputs(project, input_paths, input_hashes, implementation_hashes)
    rendered_b = _render_outputs(project, input_paths, input_hashes, implementation_hashes)
    rendered_canonical = _render_outputs(
        project, input_paths, input_hashes, implementation_hashes
    )
    for label in OUTPUTS:
        if not (
            rendered_a[label] == rendered_b[label] == rendered_canonical[label]
        ):
            _fail("N1_SAMPLER_OUTPUT_FAILURE", f"render-mismatch:{label}")

    _atomic_write(verify_a, rendered_a)
    _atomic_write(verify_b, rendered_b)
    _atomic_write(canonical, rendered_canonical)
    result: dict[str, str] = {}
    for label, relative in OUTPUTS.items():
        canonical_bytes = (canonical / relative).read_bytes()
        if (
            canonical_bytes != (verify_a / relative).read_bytes()
            or canonical_bytes != (verify_b / relative).read_bytes()
        ):
            _fail("N1_SAMPLER_OUTPUT_FAILURE", f"byte-compare:{label}")
        result[relative] = hashlib.sha256(canonical_bytes).hexdigest()
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--verification-root-a", type=Path, required=True)
    parser.add_argument("--verification-root-b", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        hashes = build_n1_sampler_contract(
            PROJECT_ROOT,
            args.output_root,
            (args.verification_root_a, args.verification_root_b),
        )
    except N1SamplerContractError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    for relative, digest in hashes.items():
        print(f"{relative} {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
