#!/usr/bin/env python3
"""Build frozen ZuCo NR stimulus identity and leakage-risk groups."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
from collections import Counter
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any, Iterable

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]
POLICY_ID = "NC_HSG_STIMULUS_GROUP_POLICY_V1"
GROUP_DOMAIN = b"NC_HSG_STIMULUS_GROUP_V1\0"
PARAPHRASE_STATUS = "NOT_VERIFIED_NO_TEXT_REVIEW"
METADATA_STATUS = "SOURCE_METADATA_NOT_AVAILABLE"
INPUTS = {
    "source_binding": (
        Path("artifacts/stimulus_source_binding_v1.yaml"),
        "d1feb8e46b69074693173594ccdc4f7c3e014ca113594701131fe460f205b941",
    ),
    "diagnostic": (
        Path("artifacts/stimulus_similarity_diagnostic_v1.yaml"),
        "878d9ea68c9f5c42cc2f8d441da3117681b354d9869e1238011f6f8d7522a66d",
    ),
    "candidates": (
        Path("artifacts/stimulus_similarity_candidates_v1.jsonl"),
        "6645369f6cfc173683c825de71d12689faa6ff75a4544c68ab018875e6d7be6b",
    ),
}
OUTPUTS = {
    "identity": Path("artifacts/stimulus_identity.yaml"),
    "groups": Path("artifacts/stimulus_groups.json"),
    "report": Path("reports/stimulus_identity.md"),
}
CANDIDATE_FIELDS = {
    "id_a", "id_b", "edit_similarity", "token_jaccard", "embedding_cosine",
    "trigger_edit_080", "trigger_jaccard_070", "trigger_embedding_070",
    "length_chars_a", "length_chars_b", "slots_a", "slots_b",
}
GROUP_KINDS = {
    "SINGLETON", "EXACT_DUPLICATE_OCCURRENCES", "NEAR_DUPLICATE_LEAKAGE_RISK",
}
FROZEN_DECISIONS = {
    (97, 327): "GROUP_LEXICAL_EQUIVALENCE_RISK",
    (307, 308): "GROUP_EMBEDDING_NEAR_DUPLICATE_LEAKAGE_RISK",
}
UNJOINED_DECISION = "UNJOINED_BELOW_FROZEN_POLICY"
HEX64 = re.compile(r"[0-9a-f]{64}")


class IdentityError(RuntimeError):
    def __init__(self, code: str, detail: str):
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}")


def _fail(code: str, detail: str) -> None:
    raise IdentityError(code, detail)


@dataclass(frozen=True)
class Expectations:
    identities: int = 344
    occurrences: int = 349
    exact_duplicate_identities: int = 5
    broad_candidates: int = 11
    final_edges: int = 2
    unjoined_candidates: int = 9
    groups: int = 342
    multi_identity_groups: int = 2
    largest_identity_component: int = 2
    singleton_groups: int = 335
    exact_duplicate_groups: int = 5
    near_duplicate_groups: int = 2
    one_occurrence_groups: int = 335
    two_occurrence_groups: int = 7
    max_group_occurrences: int = 2


DEFAULT_EXPECTATIONS = Expectations()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_policy_edge(row: dict[str, Any]) -> bool:
    return (
        row["edit_similarity"] >= 0.95
        or row["token_jaccard"] >= 0.90
        or row["embedding_cosine"] >= 0.90
    )


def stimulus_group_id(member_ids: Iterable[str]) -> str:
    members = sorted(member_ids)
    if not members or any(HEX64.fullmatch(value) is None for value in members):
        _fail("GROUP_MEMBER_ID_INVALID", repr(members))
    payload = GROUP_DOMAIN + b"\n".join(value.encode("ascii") for value in members)
    return "sg_v1_" + hashlib.sha256(payload).hexdigest()


def _reject_symlink_chain(path: Path, stop: Path, code: str, label: str) -> None:
    current = path.absolute()
    stop = stop.absolute()
    while True:
        if current.is_symlink():
            _fail(code, label)
        if current == stop or current.parent == current:
            break
        current = current.parent


def _safe_input(root: Path, relative: Path, label: str) -> Path:
    root = root.absolute()
    _reject_symlink_chain(root, Path(root.anchor), "INPUT_SYMLINK", "project_root")
    candidate = root / relative
    _reject_symlink_chain(candidate, root, "INPUT_SYMLINK", label)
    resolved_root = root.resolve()
    resolved = candidate.resolve()
    try:
        resolved.relative_to(resolved_root)
    except ValueError:
        _fail("INPUT_PATH_ESCAPE", label)
    if not resolved.is_file():
        _fail("INPUT_NOT_FILE", label)
    return resolved


def _safe_output_root(output_root: Path | None, project_root: Path) -> Path:
    if output_root is None:
        candidate = project_root.absolute()
    elif output_root.is_absolute():
        candidate = output_root.absolute()
    else:
        if ".." in output_root.parts:
            _fail("OUTPUT_PATH_ESCAPE", str(output_root))
        candidate = (project_root / output_root).absolute()
    _reject_symlink_chain(candidate, Path(candidate.anchor), "OUTPUT_SYMLINK", "output_root")
    if candidate.exists() and (candidate.is_symlink() or not candidate.is_dir()):
        _fail("OUTPUT_ROOT_INVALID", str(candidate))
    return candidate.resolve(strict=False)


def _safe_outputs(output_root: Path, inputs: dict[str, Path]) -> dict[str, Path]:
    resolved_inputs = {path.resolve() for path in inputs.values()}
    outputs: dict[str, Path] = {}
    for label, relative in OUTPUTS.items():
        candidate = output_root / relative
        _reject_symlink_chain(candidate, output_root, "OUTPUT_SYMLINK", label)
        resolved = candidate.resolve(strict=False)
        try:
            resolved.relative_to(output_root)
        except ValueError:
            _fail("OUTPUT_PATH_ESCAPE", label)
        if resolved in resolved_inputs:
            _fail("INPUT_OUTPUT_OVERLAP", label)
        outputs[label] = resolved
    if len(set(outputs.values())) != len(outputs):
        _fail("OUTPUT_PATH_DUPLICATE", "fixed outputs")
    return outputs


def _load_yaml(path: Path, label: str) -> dict[str, Any]:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        _fail("INPUT_PARSE_ERROR", f"{label}:{type(exc).__name__}")
    if not isinstance(value, dict):
        _fail("INPUT_SCHEMA_MISMATCH", label)
    return value


def _load_jsonl(path: Path, label: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    try:
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            value = json.loads(line)
            if not isinstance(value, dict):
                _fail("INPUT_SCHEMA_MISMATCH", f"{label}:{number}")
            rows.append(value)
    except IdentityError:
        raise
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        _fail("INPUT_PARSE_ERROR", f"{label}:{type(exc).__name__}")
    return rows


def _validate_source(source: dict[str, Any], expected: Expectations) -> list[dict[str, Any]]:
    if source.get("schema_version") != 1 or source.get("artifact") != "ZUCO2_NR_STIMULUS_SOURCE_BINDING_V1":
        _fail("SOURCE_SCHEMA_MISMATCH", "header")
    counts = source.get("counts", {})
    required_counts = {
        "post_practice_slots": expected.occurrences,
        "slot_hash_matches": expected.occurrences,
        "unique_exact_identities": expected.identities,
        "exact_duplicate_groups": expected.exact_duplicate_identities,
        "analysis_view_rows": 5905,
        "analysis_view_identities_covered": expected.identities,
    }
    if any(counts.get(key) != value for key, value in required_counts.items()):
        _fail("SOURCE_COUNT_MISMATCH", repr(counts))
    metadata = source.get("metadata_availability", {})
    if (
        metadata.get("document_id") is not None
        or metadata.get("paragraph_id") is not None
        or metadata.get("document_status") != METADATA_STATUS
        or metadata.get("paragraph_status") != METADATA_STATUS
        or metadata.get("block_or_line_inference_performed") is not False
    ):
        _fail("SOURCE_METADATA_MISMATCH", "availability")
    identities = source.get("identities")
    if not isinstance(identities, list) or len(identities) != expected.identities:
        _fail("SOURCE_IDENTITY_COUNT_MISMATCH", repr(type(identities)))
    ids = [row.get("exact_stimulus_id") for row in identities if isinstance(row, dict)]
    if len(ids) != len(identities) or ids != sorted(ids) or len(set(ids)) != len(ids):
        _fail("SOURCE_IDENTITY_ORDER_MISMATCH", "identities")
    all_slots: list[int] = []
    for row in identities:
        identity = row.get("exact_stimulus_id")
        if HEX64.fullmatch(str(identity)) is None or HEX64.fullmatch(str(row.get("lexical_sha256"))) is None:
            _fail("SOURCE_IDENTITY_SCHEMA_MISMATCH", str(identity))
        slots, blocks, lines = row.get("slots"), row.get("blocks"), row.get("material_lines")
        if (
            not isinstance(slots, list) or not slots or slots != sorted(slots)
            or not all(isinstance(value, int) for value in slots)
            or not isinstance(blocks, list) or len(blocks) != len(slots)
            or not isinstance(lines, list) or len(lines) != len(slots)
            or not isinstance(row.get("length_chars"), int) or row["length_chars"] <= 0
            or not isinstance(row.get("analysis_view_row_count"), int) or row["analysis_view_row_count"] <= 0
            or row.get("document_id") is not None or row.get("paragraph_id") is not None
            or row.get("document_status") != METADATA_STATUS
            or row.get("paragraph_status") != METADATA_STATUS
        ):
            _fail("SOURCE_IDENTITY_SCHEMA_MISMATCH", str(identity))
        all_slots.extend(slots)
    if sorted(all_slots) != list(range(1, expected.occurrences + 1)):
        _fail("OCCURRENCE_COVERAGE_MISMATCH", "source slots")
    duplicates = source.get("exact_duplicate_groups")
    if not isinstance(duplicates, list) or len(duplicates) != expected.exact_duplicate_identities:
        _fail("EXACT_DUPLICATE_LEDGER_MISMATCH", "count")
    by_id = {row["exact_stimulus_id"]: row for row in identities}
    duplicate_ids = sorted(identity for identity, row in by_id.items() if len(row["slots"]) > 1)
    if duplicate_ids != sorted(row.get("exact_stimulus_id") for row in duplicates):
        _fail("EXACT_DUPLICATE_LEDGER_MISMATCH", "identities")
    for row in duplicates:
        identity = row.get("exact_stimulus_id")
        if row.get("slots") != by_id[identity]["slots"] or row.get("occurrences_remain_distinct") is not True:
            _fail("EXACT_DUPLICATE_LEDGER_MISMATCH", str(identity))
    return identities


def _validate_diagnostic(
    diagnostic: dict[str, Any], source_hash: str, expected: Expectations,
) -> None:
    if diagnostic.get("schema_version") != 1 or diagnostic.get("artifact") != "ZUCO2_NR_STIMULUS_SIMILARITY_DIAGNOSTIC_V1":
        _fail("DIAGNOSTIC_SCHEMA_MISMATCH", "header")
    counts = diagnostic.get("counts", {})
    if (
        counts.get("task_slots") != expected.occurrences
        or counts.get("unique_exact_identities") != expected.identities
        or counts.get("exact_duplicate_groups") != expected.exact_duplicate_identities
        or counts.get("unordered_pairs") != 58996
        or diagnostic.get("source_binding", {}).get("sha256") != source_hash
        or diagnostic.get("broad_diagnostic_prefilter", {}).get("union_count") != expected.broad_candidates
    ):
        _fail("DIAGNOSTIC_CONTRACT_MISMATCH", "counts or source")
    policy = diagnostic.get("grouping_policy", {})
    if (
        policy.get("status") != "PENDING_GROUP_POLICY_REVIEW"
        or policy.get("final_threshold_selected") is not False
        or policy.get("near_duplicate_groups_emitted") is not False
        or policy.get("split_constructed") is not False
    ):
        _fail("DIAGNOSTIC_CONTRACT_MISMATCH", "prior policy boundary")


def _validate_candidates(
    candidates: list[dict[str, Any]], identities: list[dict[str, Any]],
    diagnostic: dict[str, Any], expected: Expectations,
) -> None:
    if len(candidates) != expected.broad_candidates:
        _fail("CANDIDATE_COUNT_MISMATCH", str(len(candidates)))
    by_id = {row["exact_stimulus_id"]: row for row in identities}
    keys: list[tuple[str, str]] = []
    trigger_counts = Counter()
    intersections = Counter()
    for number, row in enumerate(candidates, 1):
        if set(row) != CANDIDATE_FIELDS:
            _fail("CANDIDATE_SCHEMA_MISMATCH", str(number))
        left, right = row.get("id_a"), row.get("id_b")
        if left not in by_id or right not in by_id or left >= right:
            _fail("CANDIDATE_ID_MISMATCH", str(number))
        keys.append((left, right))
        for field in ("edit_similarity", "token_jaccard", "embedding_cosine"):
            value = row.get(field)
            if (
                not isinstance(value, (int, float)) or isinstance(value, bool)
                or not -1.0 <= value <= 1.0
                or Decimal(str(value)).as_tuple().exponent < -6
            ):
                _fail("CANDIDATE_SCORE_MISMATCH", f"{number}:{field}")
        expected_flags = (
            row["edit_similarity"] >= 0.80,
            row["token_jaccard"] >= 0.70,
            row["embedding_cosine"] >= 0.70,
        )
        flags = (
            row.get("trigger_edit_080"), row.get("trigger_jaccard_070"),
            row.get("trigger_embedding_070"),
        )
        if flags != expected_flags or not any(flags):
            _fail("CANDIDATE_TRIGGER_MISMATCH", str(number))
        if (
            row.get("slots_a") != by_id[left]["slots"]
            or row.get("slots_b") != by_id[right]["slots"]
            or row.get("length_chars_a") != by_id[left]["length_chars"]
            or row.get("length_chars_b") != by_id[right]["length_chars"]
        ):
            _fail("CANDIDATE_SOURCE_MISMATCH", str(number))
        names = ("edit_080", "jaccard_070", "embedding_070")
        active = [name for name, flag in zip(names, flags) if flag]
        trigger_counts.update(active)
        for first in range(len(active)):
            for second in range(first + 1, len(active)):
                intersections[f"{active[first]}__{active[second]}"] += 1
        if len(active) == 3:
            intersections["all_three"] += 1
    if keys != sorted(keys) or len(set(keys)) != len(keys):
        _fail("CANDIDATE_ORDER_MISMATCH", "id pairs")
    broad = diagnostic["broad_diagnostic_prefilter"]
    recorded_triggers = broad.get("trigger_counts", {})
    recorded_intersections = broad.get("pairwise_intersections", {})
    if any(recorded_triggers.get(key) != trigger_counts[key] for key in trigger_counts):
        _fail("CANDIDATE_DIAGNOSTIC_MISMATCH", "trigger counts")
    if any(recorded_intersections.get(key) != intersections[key] for key in recorded_intersections):
        _fail("CANDIDATE_DIAGNOSTIC_MISMATCH", "intersections")
    if broad.get("triple_intersection") != intersections["all_three"]:
        _fail("CANDIDATE_DIAGNOSTIC_MISMATCH", "triple")


def _union_components(ids: list[str], edges: list[tuple[str, str]]) -> list[list[str]]:
    parent = {identity: identity for identity in ids}

    def find(identity: str) -> str:
        while parent[identity] != identity:
            parent[identity] = parent[parent[identity]]
            identity = parent[identity]
        return identity

    for left, right in sorted(edges):
        left_root, right_root = find(left), find(right)
        if left_root == right_root:
            continue
        if left_root > right_root:
            left_root, right_root = right_root, left_root
        parent[right_root] = left_root
    grouped: dict[str, list[str]] = {}
    for identity in ids:
        grouped.setdefault(find(identity), []).append(identity)
    return sorted((sorted(members) for members in grouped.values()), key=lambda members: members[0])


def _decision_record(row: dict[str, Any], decision: str, edge: bool) -> dict[str, Any]:
    return {
        "id_a": row["id_a"], "id_b": row["id_b"],
        "slots_a": row["slots_a"], "slots_b": row["slots_b"],
        "edit_similarity": row["edit_similarity"],
        "token_jaccard": row["token_jaccard"],
        "embedding_cosine": row["embedding_cosine"],
        "meets_edit_095": row["edit_similarity"] >= 0.95,
        "meets_jaccard_090": row["token_jaccard"] >= 0.90,
        "meets_embedding_090": row["embedding_cosine"] >= 0.90,
        "policy_edge": edge,
        "decision": decision,
        "paraphrase_verified": False,
        "paraphrase_status": PARAPHRASE_STATUS,
        "document_id": None, "paragraph_id": None,
        "document_status": METADATA_STATUS, "paragraph_status": METADATA_STATUS,
    }


def _yaml_bytes(value: Any) -> bytes:
    return yaml.safe_dump(value, sort_keys=False, allow_unicode=False).encode("utf-8")


def _json_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True) + "\n").encode("utf-8")


def _report_bytes(counts: dict[str, Any]) -> bytes:
    lines = [
        "# ZuCo 2.0 NR Stimulus Identity", "",
        "## Frozen policy", "",
        f"Policy `{POLICY_ID}` groups an opaque identity pair when committed edit similarity is at least 0.95, token Jaccard is at least 0.90, or embedding cosine is at least 0.90.", "",
        "The policy uses only the committed six-decimal candidate ledger. It does not recompute scores or treat high similarity as a verified paraphrase.", "",
        "## Result", "",
        f"- Exact identities: {counts['exact_identities']}",
        f"- Preserved occurrences: {counts['occurrences']}",
        f"- Final inter-identity edges: {counts['inter_identity_edges']}",
        f"- Unjoined broad candidates: {counts['unjoined_broad_candidates']}",
        f"- Final groups: {counts['groups']}",
        f"- Group kinds: {counts['group_kinds']}",
        f"- Largest exact-ID component: {counts['largest_exact_id_component']}", "",
        "Document and paragraph metadata are unavailable. Every group and candidate remains `NOT_VERIFIED_NO_TEXT_REVIEW`.", "",
        "No stimulus text, token, n-gram, embedding vector, EEG, event, outcome, or split artifact is present. No training or Gate ran.", "",
    ]
    return "\n".join(lines).encode("utf-8")


def _atomic_write(outputs: dict[Path, bytes]) -> None:
    temporary: list[tuple[Path, Path]] = []
    try:
        for destination, content in outputs.items():
            destination.parent.mkdir(parents=True, exist_ok=True)
            descriptor, name = tempfile.mkstemp(prefix=f".{destination.name}.", dir=destination.parent)
            temp_path = Path(name)
            with os.fdopen(descriptor, "wb") as handle:
                handle.write(content)
                handle.flush()
                os.fsync(handle.fileno())
            temporary.append((temp_path, destination))
        for temp_path, destination in temporary:
            os.replace(temp_path, destination)
    finally:
        for temp_path, _ in temporary:
            temp_path.unlink(missing_ok=True)


def build(
    *,
    project_root: Path = PROJECT_ROOT,
    output_root: Path | None = None,
    expected_hashes: dict[str, str] | None = None,
    expectations: Expectations = DEFAULT_EXPECTATIONS,
) -> dict[str, Any]:
    project_root = project_root.absolute()
    hashes = expected_hashes or {label: value[1] for label, value in INPUTS.items()}
    if set(hashes) != set(INPUTS):
        _fail("INPUT_HASH_CONTRACT_MISMATCH", repr(sorted(hashes)))
    input_paths = {
        label: _safe_input(project_root, relative, label)
        for label, (relative, _) in INPUTS.items()
    }
    actual_hashes = {label: sha256_file(path) for label, path in input_paths.items()}
    for label, digest in actual_hashes.items():
        if digest != hashes[label]:
            _fail("STIMULUS_GROUP_INPUT_HASH_MISMATCH", label)
    safe_root = _safe_output_root(output_root, project_root)
    output_paths = _safe_outputs(safe_root, input_paths)

    source = _load_yaml(input_paths["source_binding"], "source_binding")
    diagnostic = _load_yaml(input_paths["diagnostic"], "diagnostic")
    candidates = _load_jsonl(input_paths["candidates"], "candidates")
    identities = _validate_source(source, expectations)
    _validate_diagnostic(diagnostic, actual_hashes["source_binding"], expectations)
    _validate_candidates(candidates, identities, diagnostic, expectations)

    decisions: list[dict[str, Any]] = []
    edges: list[tuple[str, str]] = []
    for row in candidates:
        edge = is_policy_edge(row)
        slot_pair = tuple(sorted(row["slots_a"] + row["slots_b"]))
        decision = FROZEN_DECISIONS.get(slot_pair) if edge else UNJOINED_DECISION
        if decision is None:
            _fail("FROZEN_EDGE_DECISION_MISMATCH", repr(slot_pair))
        decisions.append(_decision_record(row, decision, edge))
        if edge:
            edges.append((row["id_a"], row["id_b"]))
    if len(edges) != expectations.final_edges or len(decisions) - len(edges) != expectations.unjoined_candidates:
        _fail("POLICY_EDGE_COUNT_MISMATCH", f"{len(edges)}/{len(decisions) - len(edges)}")
    if {tuple(sorted(row["slots_a"] + row["slots_b"])) for row in decisions if row["policy_edge"]} != set(FROZEN_DECISIONS):
        _fail("FROZEN_EDGE_DECISION_MISMATCH", "edge slot pairs")

    by_id = {row["exact_stimulus_id"]: row for row in identities}
    components = _union_components(sorted(by_id), edges)
    edge_by_pair = {(row["id_a"], row["id_b"]): row for row in decisions if row["policy_edge"]}
    groups: list[dict[str, Any]] = []
    id_to_group: dict[str, tuple[str, str]] = {}
    for members in components:
        slots = sorted(slot for identity in members for slot in by_id[identity]["slots"])
        if len(members) > 1:
            kind = "NEAR_DUPLICATE_LEAKAGE_RISK"
        elif len(slots) > 1:
            kind = "EXACT_DUPLICATE_OCCURRENCES"
        else:
            kind = "SINGLETON"
        group_id = stimulus_group_id(members)
        member_set = set(members)
        edge_evidence = [
            edge_by_pair[pair]
            for pair in sorted(edge_by_pair)
            if pair[0] in member_set and pair[1] in member_set
        ]
        group = {
            "stimulus_group_id": group_id,
            "member_exact_stimulus_ids": members,
            "member_slots": slots,
            "group_kind": kind,
            "edge_decisions": edge_evidence,
            "paraphrase_verified": False,
            "paraphrase_status": PARAPHRASE_STATUS,
            "document_id": None, "paragraph_id": None,
            "document_status": METADATA_STATUS, "paragraph_status": METADATA_STATUS,
        }
        groups.append(group)
        for identity in members:
            id_to_group[identity] = (group_id, kind)

    kind_counts = Counter(group["group_kind"] for group in groups)
    occurrence_size_counts = Counter(len(group["member_slots"]) for group in groups)
    largest_component = max(len(group["member_exact_stimulus_ids"]) for group in groups)
    if (
        len(groups) != expectations.groups
        or sum(len(group["member_exact_stimulus_ids"]) > 1 for group in groups) != expectations.multi_identity_groups
        or largest_component != expectations.largest_identity_component
        or kind_counts != Counter({
            "SINGLETON": expectations.singleton_groups,
            "EXACT_DUPLICATE_OCCURRENCES": expectations.exact_duplicate_groups,
            "NEAR_DUPLICATE_LEAKAGE_RISK": expectations.near_duplicate_groups,
        })
        or occurrence_size_counts != Counter({1: expectations.one_occurrence_groups, 2: expectations.two_occurrence_groups})
        or max(occurrence_size_counts) != expectations.max_group_occurrences
        or set(kind_counts) - GROUP_KINDS
    ):
        _fail("POLICY_GROUP_COUNT_MISMATCH", repr((len(groups), kind_counts, occurrence_size_counts)))

    occurrence_rows: list[dict[str, Any]] = []
    identity_rows: list[dict[str, Any]] = []
    for row in identities:
        identity = row["exact_stimulus_id"]
        group_id, kind = id_to_group[identity]
        identity_rows.append({
            "exact_stimulus_id": identity,
            "stimulus_group_id": group_id,
            "group_kind": kind,
            "lexical_sha256": row["lexical_sha256"],
            "length_chars": row["length_chars"],
            "slots": row["slots"], "blocks": row["blocks"],
            "material_lines": row["material_lines"],
            "analysis_view_row_count": row["analysis_view_row_count"],
            "paraphrase_verified": False, "paraphrase_status": PARAPHRASE_STATUS,
            "document_id": None, "paragraph_id": None,
            "document_status": METADATA_STATUS, "paragraph_status": METADATA_STATUS,
        })
        for slot, block, material_line in zip(row["slots"], row["blocks"], row["material_lines"]):
            occurrence_rows.append({
                "slot": slot, "block": block, "material_line": material_line,
                "exact_stimulus_id": identity, "stimulus_group_id": group_id,
                "occurrence_preserved": True,
            })
    occurrence_rows.sort(key=lambda row: row["slot"])
    if [row["slot"] for row in occurrence_rows] != list(range(1, expectations.occurrences + 1)):
        _fail("OCCURRENCE_COVERAGE_MISMATCH", "output occurrences")

    exact_duplicates = []
    for row in source["exact_duplicate_groups"]:
        identity = row["exact_stimulus_id"]
        exact_duplicates.append({
            "exact_stimulus_id": identity,
            "stimulus_group_id": id_to_group[identity][0],
            "slots": row["slots"], "blocks": row["blocks"],
            "material_lines": row["material_lines"],
            "occurrences_remain_distinct": True,
        })

    counts = {
        "exact_identities": len(identity_rows),
        "occurrences": len(occurrence_rows),
        "exact_duplicate_identities": len(exact_duplicates),
        "broad_candidates": len(candidates),
        "inter_identity_edges": len(edges),
        "unjoined_broad_candidates": len(candidates) - len(edges),
        "groups": len(groups),
        "multi_exact_id_groups": sum(len(group["member_exact_stimulus_ids"]) > 1 for group in groups),
        "largest_exact_id_component": largest_component,
        "group_kinds": {kind: kind_counts[kind] for kind in sorted(GROUP_KINDS)},
        "occurrence_group_sizes": {
            "one_occurrence": occurrence_size_counts[1],
            "two_occurrences": occurrence_size_counts[2],
            "larger_than_two": sum(count for size, count in occurrence_size_counts.items() if size > 2),
        },
        "analysis_view_rows_mappable": source["counts"]["analysis_view_rows"],
    }
    input_contract = {
        label: {"path": INPUTS[label][0].as_posix(), "sha256": actual_hashes[label]}
        for label in INPUTS
    }
    policy = {
        "policy_id": POLICY_ID,
        "edge_rule": "edit_similarity >= 0.95 OR token_jaccard >= 0.90 OR embedding_cosine >= 0.90",
        "thresholds": {"edit_similarity": 0.95, "token_jaccard": 0.90, "embedding_cosine": 0.90},
        "score_source": "committed six-decimal candidate ledger",
        "rounding_contract": "compare committed values directly; do not recompute or reround",
    }
    metadata = {
        "document_id": None, "paragraph_id": None,
        "document_status": METADATA_STATUS, "paragraph_status": METADATA_STATUS,
        "block_or_line_inference_performed": False,
    }
    identity_artifact = {
        "schema_version": 1,
        "artifact": "ZUCO2_NR_STIMULUS_IDENTITY_V1",
        "policy": policy,
        "inputs": input_contract,
        "normalization_contract_reference": {
            "path": INPUTS["source_binding"][0].as_posix(),
            "sha256": actual_hashes["source_binding"],
        },
        "metadata_availability": metadata,
        "counts": counts,
        "identities": identity_rows,
        "occurrences": occurrence_rows,
        "candidate_decisions": decisions,
        "exact_duplicate_occurrences": exact_duplicates,
        "safety": {
            "stimulus_text_emitted": False, "lexical_text_emitted": False,
            "tokens_or_ngrams_emitted": False, "embedding_vectors_emitted": False,
            "eeg_event_tsr_read": False, "outcome_or_history_read": False,
            "scores_recomputed": False, "embedding_model_run": False,
            "paraphrase_review_performed": False,
        },
    }
    groups_artifact = {
        "schema_version": 1,
        "artifact": "ZUCO2_NR_STIMULUS_GROUPS_V1",
        "policy": policy,
        "inputs": input_contract,
        "counts": counts,
        "groups": groups,
        "safety": identity_artifact["safety"],
    }
    rendered = {
        output_paths["identity"]: _yaml_bytes(identity_artifact),
        output_paths["groups"]: _json_bytes(groups_artifact),
        output_paths["report"]: _report_bytes(counts),
    }
    _atomic_write(rendered)
    return {
        "identity": identity_artifact,
        "groups": groups_artifact,
        "report": rendered[output_paths["report"]],
        "output_sha256": {
            path.name: hashlib.sha256(content).hexdigest() for path, content in rendered.items()
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path)
    args = parser.parse_args(argv)
    try:
        result = build(output_root=args.output_root)
    except IdentityError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    for name, digest in sorted(result["output_sha256"].items()):
        print(f"{name} {digest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
