#!/usr/bin/env python3
"""Build the frozen NC-HSG joint split and Gate-A population contracts."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import struct
import sys
import tempfile
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SPLIT_POLICY_ID = "NC_HSG_JOINT_SPLIT_POLICY_V1"
POPULATION_POLICY_ID = "NC_HSG_GATE_A_POPULATION_V1"
PRIMARY_DOMAIN = b"NC_HSG_JOINT_SPLIT_V1\0PRIMARY\0"
CAL_DOMAIN = b"NC_HSG_JOINT_SPLIT_V1\0CAL_RESERVE\0"
BOOTSTRAP_DOMAIN = b"NC_HSG_GATE_A_POPULATION_V1\0SUBJECT_BOOTSTRAP\0"
SUBJECTS = (
    "YAC", "YAG", "YAK", "YDG", "YDR", "YFR", "YFS", "YHS", "YIS",
    "YLS", "YMD", "YMS", "YRH", "YRK", "YRP", "YSD", "YSL", "YTL",
)
PRIMARY_ROLES = ("train_fit", "inner_val", "cal", "test")
PRIMARY_CAPACITIES = (164, 41, 68, 69)
CAL_ROLES = ("cal_select_reserve", "cal_cert_reserve")
CAL_CAPACITIES = (34, 34)
INPUTS = {
    "stimulus_identity": (
        Path("artifacts/stimulus_identity.yaml"),
        "f6b94449d58c0e26d7da972968943f0eca0fa2bfc16cf2495ce8c41da80a69ea",
    ),
    "stimulus_groups": (
        Path("artifacts/stimulus_groups.json"),
        "4408e57defbdc7ac5bd503c35489d68941d231d56009550a2bb17d0973b1fded",
    ),
    "analysis_view": (
        Path("artifacts/admission/zuco2_nr_analysis_view_v1.jsonl"),
        "0751259f9f9455cba72bd7d027ffa1423e790e631ac0f5174c38da65d7cd12ff",
    ),
    "analysis_summary": (
        Path("artifacts/admission/zuco2_nr_analysis_view_v1.yaml"),
        "5e387ef3dc9e930e3ca3e4b6ccb6a009a3cc719281f1ac183cfbf56ac7b66181",
    ),
    "data_card": (
        Path("artifacts/data_card.yaml"),
        "d9331bfe34937c264b7b8c667a2b831569c4440120e1d445011aeaf419c30f84",
    ),
}
OUTPUTS = {
    "regime_i": Path("artifacts/split_regimeI.json"),
    "regime_ii": Path("artifacts/split_regimeII.json"),
    "manifest": Path("artifacts/split_manifest.yaml"),
    "population": Path("artifacts/gate_a_population.yaml"),
    "report": Path("reports/joint_split_population.md"),
}
ANALYSIS_USED_FIELDS = {
    "occurrence_id", "subject", "session", "task", "block", "slot",
    "stimulus_sha256",
}
ANALYSIS_KNOWN_FIELDS = ANALYSIS_USED_FIELDS | {
    "material_line", "raw_channels", "raw_samples", "raw_shape", "source_locator",
}
REGIME_I_ROW_FIELDS = {
    "occurrence_id", "subject", "session", "task", "block", "slot",
    "exact_stimulus_id", "stimulus_group_id", "role", "calibration_reserve",
}
EXPECTED_PRIMARY_OBJECTIVE = (201, 804726, 344, 651510, 201, 76266)
EXPECTED_PRIMARY_SWAPS = 25
EXPECTED_PRIMARY_LEDGER = "531539ff3592cc28d89c5e3ef568d019eaab733ccdb1053c1fcf1c471e9dac1c"
EXPECTED_CAL_OBJECTIVE = (34, 30056, 34, 2312, 34, 2312)
EXPECTED_CAL_SWAPS = 6
EXPECTED_CAL_LEDGER = "5f464d97e695ab6bc58d10ac2342351195fa936144487bd9e78f96e5e7a8442c"
EXPECTED_BOOTSTRAP = "e77ca92b29c414a17c1e66edf4075edd470c007dfe2019487c36758f5f99c86d"
EXPECTED_TEST_ROWS = {
    "YAC": 50, "YAG": 71, "YAK": 60, "YDG": 71, "YDR": 70, "YFR": 49,
    "YFS": 68, "YHS": 71, "YIS": 71, "YLS": 69, "YMD": 69, "YMS": 70,
    "YRH": 60, "YRK": 68, "YRP": 69, "YSD": 70, "YSL": 69, "YTL": 68,
}
EXPECTED_ROLE_SUMMARY = {
    "train_fit": (164, 167, 2832, [24, 23, 25, 24, 24, 24, 23], 117, 167),
    "inner_val": (41, 42, 709, [7, 6, 6, 6, 6, 5, 6], 29, 42),
    "cal": (68, 69, 1171, [9, 10, 10, 10, 10, 10, 10], 48, 69),
    "test": (69, 71, 1193, [10, 11, 10, 10, 10, 10, 10], 49, 71),
}
EXPECTED_CAL_SUMMARY = {
    "cal_select_reserve": (34, 35, 591, [5, 5, 5, 5, 5, 5, 5], 24, 35),
    "cal_cert_reserve": (34, 34, 580, [4, 5, 5, 5, 5, 5, 5], 24, 34),
}
HEX64 = set("0123456789abcdef")


class JointSplitError(RuntimeError):
    def __init__(self, code: str, detail: str):
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}")


def _fail(code: str, detail: str) -> None:
    raise JointSplitError(code, detail)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _is_hex64(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and set(value) <= HEX64


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


def _load_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        _fail("INPUT_PARSE_ERROR", f"{label}:{type(exc).__name__}")
    if not isinstance(value, dict):
        _fail("INPUT_SCHEMA_MISMATCH", label)
    return value


def _load_analysis_rows(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    try:
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            value = json.loads(line)
            if not isinstance(value, dict) or set(value) != ANALYSIS_KNOWN_FIELDS:
                _fail("ANALYSIS_ROW_FIELD_MISMATCH", str(number))
            rows.append({key: value[key] for key in ANALYSIS_USED_FIELDS})
    except JointSplitError:
        raise
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        _fail("INPUT_PARSE_ERROR", f"analysis_view:{type(exc).__name__}")
    return rows


@dataclass(frozen=True)
class DataBundle:
    identity: dict[str, Any]
    groups_artifact: dict[str, Any]
    groups: tuple[dict[str, Any], ...]
    rows: tuple[dict[str, Any], ...]
    slot_records: dict[int, dict[str, Any]]
    features: dict[str, tuple[int, ...]]


@dataclass(frozen=True)
class AssignmentResult:
    assignments: dict[str, str]
    iterations: int
    objective: tuple[int, int, int, int, int, int]
    ledger_sha256: str
    initial_order_sha256: str


def _validate_inputs(
    identity: dict[str, Any], groups_artifact: dict[str, Any],
    rows: list[dict[str, Any]], summary: dict[str, Any], card: dict[str, Any],
) -> DataBundle:
    if identity.get("schema_version") != 1 or identity.get("artifact") != "ZUCO2_NR_STIMULUS_IDENTITY_V1":
        _fail("IDENTITY_SCHEMA_MISMATCH", "header")
    if groups_artifact.get("schema_version") != 1 or groups_artifact.get("artifact") != "ZUCO2_NR_STIMULUS_GROUPS_V1":
        _fail("GROUP_SCHEMA_MISMATCH", "header")
    if identity.get("policy", {}).get("policy_id") != "NC_HSG_STIMULUS_GROUP_POLICY_V1":
        _fail("IDENTITY_POLICY_MISMATCH", "policy_id")
    if groups_artifact.get("policy", {}).get("policy_id") != "NC_HSG_STIMULUS_GROUP_POLICY_V1":
        _fail("GROUP_POLICY_MISMATCH", "policy_id")
    required_counts = {
        "exact_identities": 344, "occurrences": 349, "groups": 342,
        "multi_exact_id_groups": 2, "largest_exact_id_component": 2,
    }
    for artifact, label in ((identity, "identity"), (groups_artifact, "groups")):
        counts = artifact.get("counts", {})
        if any(counts.get(key) != value for key, value in required_counts.items()):
            _fail("JOINT_SPLIT_INPUT_COUNT_MISMATCH", label)

    identities = identity.get("identities")
    occurrences = identity.get("occurrences")
    groups = groups_artifact.get("groups")
    if not isinstance(identities, list) or not isinstance(occurrences, list) or not isinstance(groups, list):
        _fail("JOINT_SPLIT_INPUT_SCHEMA_MISMATCH", "identity/groups lists")
    if len(identities) != 344 or len(occurrences) != 349 or len(groups) != 342:
        _fail("JOINT_SPLIT_INPUT_COUNT_MISMATCH", "identity/groups lengths")
    identity_ids = [row.get("exact_stimulus_id") for row in identities]
    if identity_ids != sorted(identity_ids) or len(set(identity_ids)) != 344 or not all(_is_hex64(value) for value in identity_ids):
        _fail("IDENTITY_ORDER_MISMATCH", "identities")
    group_ids = [row.get("stimulus_group_id") for row in groups]
    if len(set(group_ids)) != 342:
        _fail("GROUP_ID_MISMATCH", "duplicate group IDs")
    if not all(isinstance(value, str) and value.startswith("sg_v1_") and _is_hex64(value[6:]) for value in group_ids):
        _fail("GROUP_ID_MISMATCH", "group IDs")

    identity_to_group: dict[str, str] = {}
    for row in identities:
        exact_id = row.get("exact_stimulus_id")
        group_id = row.get("stimulus_group_id")
        if group_id not in set(group_ids):
            _fail("IDENTITY_GROUP_COVERAGE_MISMATCH", str(exact_id))
        identity_to_group[exact_id] = group_id
    member_ids: list[str] = []
    group_by_id: dict[str, dict[str, Any]] = {}
    for row in groups:
        group_id = row["stimulus_group_id"]
        members = row.get("member_exact_stimulus_ids")
        slots = row.get("member_slots")
        if not isinstance(members, list) or members != sorted(members) or not isinstance(slots, list) or slots != sorted(slots):
            _fail("GROUP_MEMBER_ORDER_MISMATCH", group_id)
        if any(identity_to_group.get(member) != group_id for member in members):
            _fail("IDENTITY_GROUP_COVERAGE_MISMATCH", group_id)
        member_ids.extend(members)
        group_by_id[group_id] = row
    if groups != sorted(groups, key=lambda row: row["member_exact_stimulus_ids"][0]):
        _fail("GROUP_ORDER_MISMATCH", "minimum member exact ID")
    if sorted(member_ids) != identity_ids:
        _fail("IDENTITY_GROUP_COVERAGE_MISMATCH", "all identities")

    slot_records: dict[int, dict[str, Any]] = {}
    for row in occurrences:
        slot = row.get("slot")
        exact_id = row.get("exact_stimulus_id")
        group_id = row.get("stimulus_group_id")
        block = row.get("block")
        if (
            not isinstance(slot, int) or not 1 <= slot <= 349
            or not isinstance(block, int) or not 1 <= block <= 7
            or identity_to_group.get(exact_id) != group_id
            or row.get("occurrence_preserved") is not True
            or slot in slot_records
        ):
            _fail("OCCURRENCE_MAPPING_MISMATCH", repr(slot))
        slot_records[slot] = {"exact_stimulus_id": exact_id, "stimulus_group_id": group_id, "block": block}
    if sorted(slot_records) != list(range(1, 350)):
        _fail("OCCURRENCE_COVERAGE_MISMATCH", "slots")
    for group_id, group in group_by_id.items():
        expected_slots = sorted(slot for slot, value in slot_records.items() if value["stimulus_group_id"] == group_id)
        if group.get("member_slots") != expected_slots:
            _fail("GROUP_SLOT_COVERAGE_MISMATCH", group_id)

    if len(rows) != 5905:
        _fail("ANALYSIS_ROW_COUNT_MISMATCH", str(len(rows)))
    row_keys = [(row["subject"], row["slot"], row["occurrence_id"]) for row in rows]
    if row_keys != sorted(row_keys) or len(set((row["subject"], row["slot"]) for row in rows)) != 5905:
        _fail("ANALYSIS_ROW_ORDER_MISMATCH", "canonical row order or subject-slot keys")
    slot_occurrence_ids: dict[int, set[str]] = defaultdict(set)
    for row in rows:
        slot_occurrence_ids[row["slot"]].add(row["occurrence_id"])
    if (
        sorted(slot_occurrence_ids) != list(range(1, 350))
        or any(len(values) != 1 for values in slot_occurrence_ids.values())
        or len({next(iter(values)) for values in slot_occurrence_ids.values()}) != 349
    ):
        _fail("ANALYSIS_OCCURRENCE_ID_MISMATCH", "slot-to-occurrence mapping")
    subject_counts: Counter[str] = Counter()
    exact_row_counts: Counter[str] = Counter()
    group_subject_counts: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        slot = row.get("slot")
        subject = row.get("subject")
        occurrence = slot_records.get(slot)
        if (
            subject not in SUBJECTS or row.get("session") != 1 or row.get("task") != "NR"
            or occurrence is None or row.get("block") != occurrence["block"]
            or row.get("stimulus_sha256") != occurrence["exact_stimulus_id"]
        ):
            _fail("ANALYSIS_ROW_MAPPING_MISMATCH", str(row.get("occurrence_id")))
        subject_counts[subject] += 1
        exact_row_counts[occurrence["exact_stimulus_id"]] += 1
        group_subject_counts[occurrence["stimulus_group_id"]][subject] += 1
    if tuple(subject for subject in SUBJECTS if subject_counts[subject]) != SUBJECTS:
        _fail("SUBJECT_ORDER_MISMATCH", repr(sorted(subject_counts)))
    for row in identities:
        if row.get("analysis_view_row_count") != exact_row_counts[row["exact_stimulus_id"]]:
            _fail("ANALYSIS_IDENTITY_ROW_COUNT_MISMATCH", row["exact_stimulus_id"])

    if summary.get("counts", {}).get("admitted") != 5905 or summary.get("analysis_view_admission", {}).get("status") != "PASS":
        _fail("ANALYSIS_SUMMARY_MISMATCH", "admission")
    composition = card.get("composition", {})
    card_view = card.get("analysis_view", {})
    if (
        composition.get("subject_ids") != list(SUBJECTS)
        or composition.get("subjects") != 18 or composition.get("sessions") != 1
        or composition.get("task") != "NR" or composition.get("blocks") != 7
        or composition.get("slots_per_subject") != 349
        or card_view.get("status") != "PASS" or card_view.get("counts", {}).get("admitted") != 5905
    ):
        _fail("DATA_CARD_MISMATCH", "composition/admission")

    features: dict[str, tuple[int, ...]] = {}
    for group_id in group_ids:
        group = group_by_id[group_id]
        subject_features = [group_subject_counts[group_id][subject] for subject in SUBJECTS]
        block_features = [0] * 7
        for slot in group["member_slots"]:
            block_features[slot_records[slot]["block"] - 1] += 1
        occurrence_count = len(group["member_slots"])
        vector = tuple(subject_features + block_features + [occurrence_count])
        if len(vector) != 26 or any(not isinstance(value, int) or value < 0 for value in vector):
            _fail("GROUP_FEATURE_MISMATCH", group_id)
        features[group_id] = vector
    if sum(sum(vector[:18]) for vector in features.values()) != 5905:
        _fail("GROUP_FEATURE_MISMATCH", "row total")
    if sum(vector[25] for vector in features.values()) != 349:
        _fail("GROUP_FEATURE_MISMATCH", "occurrence total")

    return DataBundle(
        identity=identity,
        groups_artifact=groups_artifact,
        groups=tuple(groups), rows=tuple(rows), slot_records=slot_records, features=features,
    )


def _canonical_assignment_ledger(assignments: dict[str, str]) -> bytes:
    return "".join(f"{group_id}\t{assignments[group_id]}\n" for group_id in sorted(assignments)).encode("utf-8")


def _objective(
    observed: Sequence[Sequence[int]], totals: Sequence[int],
    capacities: Sequence[int], n: int,
) -> tuple[int, int, int, int, int, int]:
    deviations = [
        [abs(n * role_values[d] - capacities[r] * totals[d]) for d in range(26)]
        for r, role_values in enumerate(observed)
    ]
    values: list[int] = []
    for start, end in ((0, 18), (18, 25), (25, 26)):
        category = [deviations[r][d] for r in range(len(capacities)) for d in range(start, end)]
        values.extend((max(category), sum(value * value for value in category)))
    return tuple(values)  # type: ignore[return-value]


def _candidate_objective(
    observed: Sequence[Sequence[int]], totals: Sequence[int], capacities: Sequence[int], n: int,
    current_deviations: Sequence[Sequence[int]], current_sums: Sequence[int],
    unaffected_max: Sequence[int], role_a: int, role_b: int,
    feature_a: Sequence[int], feature_b: Sequence[int],
) -> tuple[int, int, int, int, int, int]:
    new_a = [observed[role_a][d] - feature_a[d] + feature_b[d] for d in range(26)]
    new_b = [observed[role_b][d] - feature_b[d] + feature_a[d] for d in range(26)]
    dev_a = [abs(n * new_a[d] - capacities[role_a] * totals[d]) for d in range(26)]
    dev_b = [abs(n * new_b[d] - capacities[role_b] * totals[d]) for d in range(26)]
    result: list[int] = []
    for category, (start, end) in enumerate(((0, 18), (18, 25), (25, 26))):
        maximum = max(unaffected_max[category], max(dev_a[start:end]), max(dev_b[start:end]))
        squares = current_sums[category]
        squares -= sum(current_deviations[role_a][d] ** 2 for d in range(start, end))
        squares -= sum(current_deviations[role_b][d] ** 2 for d in range(start, end))
        squares += sum(dev_a[d] ** 2 + dev_b[d] ** 2 for d in range(start, end))
        result.extend((maximum, squares))
    return tuple(result)  # type: ignore[return-value]


def balance_assignment(
    features: dict[str, tuple[int, ...]], roles: Sequence[str], capacities: Sequence[int], domain: bytes,
) -> AssignmentResult:
    if len(roles) != len(capacities) or sum(capacities) != len(features) or any(value <= 0 for value in capacities):
        _fail("ASSIGNMENT_CAPACITY_MISMATCH", repr((roles, capacities, len(features))))
    if any(len(vector) != 26 or any(not isinstance(value, int) or value < 0 for value in vector) for vector in features.values()):
        _fail("ASSIGNMENT_FEATURE_MISMATCH", "features")
    ordered = sorted(features, key=lambda group_id: (hashlib.sha256(domain + group_id.encode("ascii")).digest(), group_id))
    initial_order_hash = sha256_bytes("".join(f"{group_id}\n" for group_id in ordered).encode("ascii"))
    assignments: dict[str, str] = {}
    cursor = 0
    for role, capacity in zip(roles, capacities):
        for group_id in ordered[cursor:cursor + capacity]:
            assignments[group_id] = role
        cursor += capacity
    role_index = {role: index for index, role in enumerate(roles)}
    totals = [sum(vector[d] for vector in features.values()) for d in range(26)]
    observed = [[0] * 26 for _ in roles]
    for group_id, role in assignments.items():
        index = role_index[role]
        for d, value in enumerate(features[group_id]):
            observed[index][d] += value

    group_ids = sorted(features)
    iterations = 0
    while True:
        current = _objective(observed, totals, capacities, len(features))
        deviations = [
            [abs(len(features) * observed[r][d] - capacities[r] * totals[d]) for d in range(26)]
            for r in range(len(roles))
        ]
        current_sums = [
            sum(deviations[r][d] ** 2 for r in range(len(roles)) for d in range(start, end))
            for start, end in ((0, 18), (18, 25), (25, 26))
        ]
        unaffected: dict[tuple[int, int], tuple[int, int, int]] = {}
        for role_a in range(len(roles)):
            for role_b in range(role_a + 1, len(roles)):
                remaining = [r for r in range(len(roles)) if r not in (role_a, role_b)]
                values = []
                for start, end in ((0, 18), (18, 25), (25, 26)):
                    values.append(max((deviations[r][d] for r in remaining for d in range(start, end)), default=0))
                unaffected[(role_a, role_b)] = tuple(values)  # type: ignore[assignment]

        best_objective = current
        best_pair: tuple[str, str] | None = None
        for i, group_a in enumerate(group_ids):
            role_a = role_index[assignments[group_a]]
            for group_b in group_ids[i + 1:]:
                role_b = role_index[assignments[group_b]]
                if role_a == role_b:
                    continue
                pair = (min(role_a, role_b), max(role_a, role_b))
                candidate = _candidate_objective(
                    observed, totals, capacities, len(features), deviations, current_sums,
                    unaffected[pair], role_a, role_b, features[group_a], features[group_b],
                )
                if candidate < best_objective:
                    best_objective = candidate
                    best_pair = (group_a, group_b)
        if best_pair is None:
            break
        group_a, group_b = best_pair
        role_a = role_index[assignments[group_a]]
        role_b = role_index[assignments[group_b]]
        for d in range(26):
            delta = features[group_b][d] - features[group_a][d]
            observed[role_a][d] += delta
            observed[role_b][d] -= delta
        assignments[group_a], assignments[group_b] = assignments[group_b], assignments[group_a]
        if _objective(observed, totals, capacities, len(features)) != best_objective:
            _fail("ASSIGNMENT_OBJECTIVE_MISMATCH", "incremental update")
        iterations += 1
        if iterations > len(features) * len(features):
            _fail("ASSIGNMENT_NONTERMINATION", str(iterations))

    ledger_hash = sha256_bytes(_canonical_assignment_ledger(assignments))
    return AssignmentResult(
        assignments=assignments, iterations=iterations,
        objective=_objective(observed, totals, capacities, len(features)),
        ledger_sha256=ledger_hash, initial_order_sha256=initial_order_hash,
    )


def bootstrap_index_hash(replicates: int = 10_000, draws: int = 18) -> tuple[str, int]:
    if replicates != 10_000 or draws != 18:
        _fail("BOOTSTRAP_CONTRACT_MISMATCH", f"{replicates}/{draws}")
    limit = ((1 << 64) // 18) * 18
    output = bytearray()
    retries = 0
    for replicate in range(replicates):
        for draw in range(draws):
            retry = 0
            while True:
                digest = hashlib.sha256(BOOTSTRAP_DOMAIN + struct.pack(">IHH", replicate, draw, retry)).digest()
                value = int.from_bytes(digest[:8], "big")
                if value < limit:
                    output.append(value % 18)
                    retries += retry
                    break
                retry += 1
                if retry > 0xFFFF:
                    _fail("BOOTSTRAP_RETRY_OVERFLOW", f"{replicate}/{draw}")
    if len(output) != 180_000:
        _fail("BOOTSTRAP_BYTE_COUNT_MISMATCH", str(len(output)))
    return sha256_bytes(bytes(output)), retries


def _role_summary(
    bundle: DataBundle, assignments: dict[str, str], roles: Sequence[str],
    reserve_assignments: dict[str, str] | None = None,
) -> dict[str, dict[str, Any]]:
    group_counts = Counter(assignments.values())
    occurrence_counts: Counter[str] = Counter()
    row_counts: Counter[str] = Counter()
    blocks: dict[str, list[int]] = {role: [0] * 7 for role in roles}
    subject_rows: dict[str, Counter[str]] = {role: Counter() for role in roles}
    for group in sorted(bundle.groups, key=lambda row: row["stimulus_group_id"]):
        group_id = group["stimulus_group_id"]
        if group_id not in assignments:
            continue
        role = assignments[group_id]
        occurrence_counts[role] += len(group["member_slots"])
        for slot in group["member_slots"]:
            blocks[role][bundle.slot_records[slot]["block"] - 1] += 1
    for row in bundle.rows:
        group_id = bundle.slot_records[row["slot"]]["stimulus_group_id"]
        if group_id not in assignments:
            continue
        role = assignments[group_id]
        row_counts[role] += 1
        subject_rows[role][row["subject"]] += 1
    result: dict[str, dict[str, Any]] = {}
    for role in roles:
        values = [subject_rows[role][subject] for subject in SUBJECTS]
        result[role] = {
            "groups": group_counts[role], "occurrences": occurrence_counts[role],
            "analysis_rows": row_counts[role], "block_occurrences": blocks[role],
            "per_subject_row_min": min(values), "per_subject_row_max": max(values),
        }
    return result


def _assert_summary(
    actual: dict[str, dict[str, Any]],
    expected: dict[str, tuple[int, int, int, list[int], int, int]], label: str,
) -> None:
    for role, values in expected.items():
        expected_groups, expected_occurrences, expected_rows, expected_blocks, expected_min, expected_max = values
        row = actual.get(role, {})
        if (
            row.get("groups") != expected_groups or row.get("occurrences") != expected_occurrences
            or row.get("analysis_rows") != expected_rows or row.get("block_occurrences") != expected_blocks
            or row.get("per_subject_row_min") != expected_min or row.get("per_subject_row_max") != expected_max
        ):
            _fail("FIXED_SUMMARY_MISMATCH", f"{label}:{role}:{row}")


def _regime_i(
    bundle: DataBundle, primary: AssignmentResult, reserve: AssignmentResult,
    input_contract: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    group_records: list[dict[str, Any]] = []
    exact_ids: list[str] = []
    slots: list[int] = []
    for group in sorted(bundle.groups, key=lambda row: row["stimulus_group_id"]):
        group_id = group["stimulus_group_id"]
        role = primary.assignments[group_id]
        calibration_reserve = reserve.assignments.get(group_id) if role == "cal" else None
        record = {
            "stimulus_group_id": group_id,
            "member_exact_stimulus_ids": group["member_exact_stimulus_ids"],
            "member_slots": group["member_slots"],
            "role": role,
            "calibration_reserve": calibration_reserve,
        }
        group_records.append(record)
        exact_ids.extend(record["member_exact_stimulus_ids"])
        slots.extend(record["member_slots"])
    if len(group_records) != 342 or len(set(exact_ids)) != 344 or sorted(slots) != list(range(1, 350)):
        _fail("REGIME_I_GROUP_COVERAGE_MISMATCH", "groups/exact IDs/slots")
    role_sets = {role: {row["stimulus_group_id"] for row in group_records if row["role"] == role} for role in PRIMARY_ROLES}
    if any(role_sets[a] & role_sets[b] for i, a in enumerate(PRIMARY_ROLES) for b in PRIMARY_ROLES[i + 1:]):
        _fail("REGIME_I_GROUP_OVERLAP", "roles")

    row_records: list[dict[str, Any]] = []
    subject_role_counts: dict[str, Counter[str]] = {subject: Counter() for subject in SUBJECTS}
    row_keys: set[tuple[str, int]] = set()
    occurrence_ids: set[str] = set()
    for row in bundle.rows:
        slot_record = bundle.slot_records[row["slot"]]
        group_id = slot_record["stimulus_group_id"]
        role = primary.assignments[group_id]
        record = {
            "occurrence_id": row["occurrence_id"], "subject": row["subject"],
            "session": row["session"], "task": row["task"], "block": row["block"],
            "slot": row["slot"], "exact_stimulus_id": slot_record["exact_stimulus_id"],
            "stimulus_group_id": group_id, "role": role,
            "calibration_reserve": reserve.assignments.get(group_id) if role == "cal" else None,
        }
        if set(record) != REGIME_I_ROW_FIELDS:
            _fail("REGIME_I_ROW_FIELD_MISMATCH", str(row["occurrence_id"]))
        row_records.append(record)
        subject_role_counts[row["subject"]][role] += 1
        row_keys.add((row["subject"], row["slot"]))
        occurrence_ids.add(row["occurrence_id"])
    row_records.sort(key=lambda row: (row["subject"], row["slot"], row["occurrence_id"]))
    if len(row_records) != 5905 or len(row_keys) != 5905 or len(occurrence_ids) != 349:
        _fail("REGIME_I_ROW_COVERAGE_MISMATCH", str(len(row_records)))
    if any(subject_role_counts[subject][role] == 0 for subject in SUBJECTS for role in PRIMARY_ROLES):
        _fail("REGIME_I_SUBJECT_COVERAGE_MISMATCH", "empty subject role")

    summary = _role_summary(bundle, primary.assignments, PRIMARY_ROLES)
    _assert_summary(summary, EXPECTED_ROLE_SUMMARY, "primary")
    artifact = {
        "schema_version": 1,
        "artifact": "ZUCO2_NR_SPLIT_REGIME_I_V1",
        "policy_id": SPLIT_POLICY_ID,
        "inputs": input_contract,
        "role_order": list(PRIMARY_ROLES),
        "capacities": dict(zip(PRIMARY_ROLES, PRIMARY_CAPACITIES)),
        "outer_train_roles": ["train_fit", "inner_val"],
        "test_status": "LOCKED_UNTIL_ROUTE_LOCK",
        "group_assignment_ledger_sha256": primary.ledger_sha256,
        "calibration_reserve_ledger_sha256": reserve.ledger_sha256,
        "counts": {
            "groups": 342, "exact_stimulus_ids": 344, "stimulus_occurrences": 349,
            "analysis_rows": 5905, "subjects": 18,
        },
        "role_summary": summary,
        "group_assignments": group_records,
        "row_assignments": row_records,
    }
    return artifact, summary


def _fold_status(subject: str, group_role: str, held_out: str) -> str:
    if subject != held_out and group_role in ("train_fit", "inner_val", "cal"):
        return group_role
    if subject == held_out and group_role == "test":
        return "test"
    if subject == held_out:
        return "excluded_heldout_non_test"
    return "excluded_nonheldout_test"


def _regime_ii(
    bundle: DataBundle, primary: AssignmentResult, reserve: AssignmentResult,
    input_contract: dict[str, Any],
) -> dict[str, Any]:
    canonical_rows = sorted(bundle.rows, key=lambda row: (row["subject"], row["slot"], row["occurrence_id"]))
    folds: list[dict[str, Any]] = []
    status_names = (
        "train_fit", "inner_val", "cal", "test",
        "excluded_heldout_non_test", "excluded_nonheldout_test",
    )
    for held_out in SUBJECTS:
        fold_id = f"loso_{held_out}"
        counts: Counter[str] = Counter()
        reserve_counts: Counter[str] = Counter()
        test_ids: list[str] = []
        ledger = bytearray()
        for row in canonical_rows:
            group_id = bundle.slot_records[row["slot"]]["stimulus_group_id"]
            group_role = primary.assignments[group_id]
            status = _fold_status(row["subject"], group_role, held_out)
            counts[status] += 1
            if status == "cal":
                reserve_counts[reserve.assignments[group_id]] += 1
            if status == "test":
                test_ids.append(row["occurrence_id"])
                if row["subject"] != held_out or group_role != "test":
                    _fail("REGIME_II_TEST_LEAKAGE", fold_id)
            if status in ("train_fit", "inner_val", "cal") and (row["subject"] == held_out or group_role == "test"):
                _fail("REGIME_II_TRAIN_LEAKAGE", fold_id)
            ledger.extend(f"{fold_id}\t{row['occurrence_id']}\t{status}\n".encode("utf-8"))
        if sum(counts.values()) != 5905 or set(counts) != set(status_names):
            _fail("REGIME_II_STATUS_COVERAGE_MISMATCH", fold_id)
        if not (2665 <= counts["train_fit"] <= 2715 and 667 <= counts["inner_val"] <= 680 and 1102 <= counts["cal"] <= 1123 and 49 <= counts["test"] <= 71):
            _fail("REGIME_II_FIXED_RANGE_MISMATCH", f"{fold_id}:{dict(counts)}")
        folds.append({
            "fold_id": fold_id,
            "held_out_subject": held_out,
            "train_subjects": [subject for subject in SUBJECTS if subject != held_out],
            "partition_predicates": {
                "train_fit": "subject != held_out AND group_role == train_fit",
                "inner_val": "subject != held_out AND group_role == inner_val",
                "cal": "subject != held_out AND group_role == cal",
                "test": "subject == held_out AND group_role == test",
                "excluded_heldout_non_test": "subject == held_out AND group_role != test",
                "excluded_nonheldout_test": "subject != held_out AND group_role == test",
            },
            "counts": {status: counts[status] for status in status_names},
            "calibration_reserve_row_counts": {role: reserve_counts[role] for role in CAL_ROLES},
            "test_occurrence_ids": sorted(test_ids),
            "canonical_membership_ledger_sha256": sha256_bytes(bytes(ledger)),
        })
    if [fold["held_out_subject"] for fold in folds] != list(SUBJECTS) or any(not fold["test_occurrence_ids"] for fold in folds):
        _fail("REGIME_II_FOLD_COVERAGE_MISMATCH", "subjects/test")
    return {
        "schema_version": 1,
        "artifact": "ZUCO2_NR_SPLIT_REGIME_II_V1",
        "policy_id": SPLIT_POLICY_ID,
        "inputs": input_contract,
        "shared_group_assignment_ledger_sha256": primary.ledger_sha256,
        "shared_calibration_reserve_ledger_sha256": reserve.ledger_sha256,
        "interpretation": "EMPIRICAL_EXTERNAL_VALIDITY_ONLY",
        "test_status": "LOCKED_UNTIL_ROUTE_LOCK",
        "fold_count": 18,
        "canonical_input_row_count_per_fold": 5905,
        "folds": folds,
    }


def _population(regime_i: dict[str, Any], regime_ii: dict[str, Any]) -> dict[str, Any]:
    actual_test_rows = Counter(row["subject"] for row in regime_i["row_assignments"] if row["role"] == "test")
    if dict(actual_test_rows) != EXPECTED_TEST_ROWS:
        _fail("GATE_A_POPULATION_COUNT_MISMATCH", repr(dict(actual_test_rows)))
    bootstrap_hash, retry_count = bootstrap_index_hash()
    if bootstrap_hash != EXPECTED_BOOTSTRAP:
        _fail("BOOTSTRAP_HASH_MISMATCH", bootstrap_hash)
    return {
        "schema_version": 1,
        "artifact": "NC_HSG_GATE_A_POPULATION_V1",
        "policy_id": POPULATION_POLICY_ID,
        "regime_i_confirmatory_population": {
            "subjects": list(SUBJECTS),
            "cluster_unit": "subject",
            "weighting": "EQUAL_WEIGHT_SUBJECT_MACRO",
            "test_rows_by_subject": {subject: actual_test_rows[subject] for subject in SUBJECTS},
            "test_status": "LOCKED_UNTIL_ROUTE_LOCK",
        },
        "regime_ii_descriptive_population": {
            "fold_ids": [fold["fold_id"] for fold in regime_ii["folds"]],
            "held_out_subjects": list(SUBJECTS),
            "weighting": "EQUAL_WEIGHT_HELDOUT_FOLD_MACRO",
            "interpretation": "EMPIRICAL_EXTERNAL_VALIDITY_ONLY",
        },
        "aggregation_contract": {
            "order": [
                "trial_to_subject_on_fixed_common_rows",
                "average_five_seeds_within_subject",
                "equal_weight_mean_across_18_subjects",
            ],
            "paired_indices": ["row", "subject", "seed"],
            "independent_cluster_allowlist": ["subject"],
            "missing_frozen_subject_action": "CONFIRMATORY_GATE_NOT_EVALUABLE",
            "zero_fill": False,
            "silent_subject_deletion": False,
        },
        "paired_subject_bootstrap": {
            "replicates": 10_000,
            "draws_per_replicate": 18,
            "subject_order": list(SUBJECTS),
            "domain_hex": BOOTSTRAP_DOMAIN.hex(),
            "counter_encoding": "uint32_be(replicate)+uint16_be(draw)+uint16_be(retry)",
            "rejection_limit": ((1 << 64) // 18) * 18,
            "index_encoding": "180000 uint8 bytes in replicate/draw order",
            "index_bytes_sha256": bootstrap_hash,
            "total_retries": retry_count,
            "binary_indices_committed": False,
            "confidence_interval": "paired equal-tailed 2.5/97.5 percent subject bootstrap",
        },
        "execution_state": {
            "scientific_statistics_computed": False,
            "gate_executed": False,
        },
    }


def _json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=True, sort_keys=True, indent=2) + "\n").encode("utf-8")


def _yaml_bytes(value: Any) -> bytes:
    return yaml.safe_dump(value, allow_unicode=False, sort_keys=False, width=120).encode("utf-8")


def _report_bytes(
    primary: AssignmentResult, reserve: AssignmentResult,
    summary: dict[str, dict[str, Any]], population: dict[str, Any],
) -> bytes:
    lines = [
        "# ZuCo 2.0 NR Joint Split and Gate-A Population", "",
        "## Frozen assignment", "",
        f"Policy `{SPLIT_POLICY_ID}` uses fixed hash initialization and integer pair-swap balancing. No seed or alternative split was searched.", "",
        f"- Primary swaps: {primary.iterations}",
        f"- Primary objective: {primary.objective}",
        f"- Primary ledger SHA256: `{primary.ledger_sha256}`",
        f"- Calibration-reserve swaps: {reserve.iterations}",
        f"- Calibration-reserve objective: {reserve.objective}",
        f"- Calibration-reserve ledger SHA256: `{reserve.ledger_sha256}`", "",
        "## Regime I", "",
    ]
    for role in PRIMARY_ROLES:
        row = summary[role]
        lines.append(f"- {role}: {row['groups']} groups, {row['occurrences']} occurrences, {row['analysis_rows']} rows")
    lines.extend([
        "", "All 342 groups and 5,905 admitted assignment rows are covered once. Test identities are `LOCKED_UNTIL_ROUTE_LOCK`.", "",
        "## Regime II and population", "",
        "Regime II contains 18 LOSO folds that reuse the frozen group roles and prohibit held-out-subject adaptation.",
        f"Gate-A population policy `{POPULATION_POLICY_ID}` freezes equal-weight subject macro aggregation and a 10,000 x 18 paired subject bootstrap.",
        f"Bootstrap index-byte SHA256: `{population['paired_subject_bootstrap']['index_bytes_sha256']}`", "",
        "No random split, source text, raw signal metadata, scientific statistic, test result, training, backbone selection, leakage audit, or Gate execution is present.", "",
    ])
    return "\n".join(lines).encode("utf-8")


def _atomic_write(outputs: dict[Path, bytes]) -> None:
    temporary: list[tuple[Path, Path]] = []
    try:
        for destination, content in outputs.items():
            destination.parent.mkdir(parents=True, exist_ok=True)
            if destination.is_symlink():
                _fail("OUTPUT_SYMLINK", destination.name)
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
    *, project_root: Path = PROJECT_ROOT, output_root: Path | None = None,
    expected_hashes: dict[str, str] | None = None,
) -> dict[str, Any]:
    project_root = project_root.absolute()
    hashes = expected_hashes or {label: contract[1] for label, contract in INPUTS.items()}
    if set(hashes) != set(INPUTS):
        _fail("INPUT_HASH_CONTRACT_MISMATCH", repr(sorted(hashes)))
    input_paths = {label: _safe_input(project_root, contract[0], label) for label, contract in INPUTS.items()}
    actual_hashes = {label: sha256_file(path) for label, path in input_paths.items()}
    for label, digest in actual_hashes.items():
        if digest != hashes[label]:
            _fail("JOINT_SPLIT_INPUT_HASH_MISMATCH", label)
    safe_root = _safe_output_root(output_root, project_root)
    output_paths = _safe_outputs(safe_root, input_paths)

    identity = _load_yaml(input_paths["stimulus_identity"], "stimulus_identity")
    groups = _load_json(input_paths["stimulus_groups"], "stimulus_groups")
    rows = _load_analysis_rows(input_paths["analysis_view"])
    summary = _load_yaml(input_paths["analysis_summary"], "analysis_summary")
    card = _load_yaml(input_paths["data_card"], "data_card")
    bundle = _validate_inputs(identity, groups, rows, summary, card)
    input_contract = {
        label: {"path": INPUTS[label][0].as_posix(), "sha256": actual_hashes[label]}
        for label in INPUTS
    }

    primary = balance_assignment(bundle.features, PRIMARY_ROLES, PRIMARY_CAPACITIES, PRIMARY_DOMAIN)
    if (
        primary.iterations != EXPECTED_PRIMARY_SWAPS
        or primary.objective != EXPECTED_PRIMARY_OBJECTIVE
        or primary.ledger_sha256 != EXPECTED_PRIMARY_LEDGER
    ):
        _fail("PRIMARY_ASSIGNMENT_FIXED_ASSERTION_MISMATCH", repr(primary))
    cal_features = {group_id: bundle.features[group_id] for group_id, role in primary.assignments.items() if role == "cal"}
    reserve = balance_assignment(cal_features, CAL_ROLES, CAL_CAPACITIES, CAL_DOMAIN)
    if (
        reserve.iterations != EXPECTED_CAL_SWAPS
        or reserve.objective != EXPECTED_CAL_OBJECTIVE
        or reserve.ledger_sha256 != EXPECTED_CAL_LEDGER
    ):
        _fail("CAL_ASSIGNMENT_FIXED_ASSERTION_MISMATCH", repr(reserve))

    regime_i, role_summary = _regime_i(bundle, primary, reserve, input_contract)
    cal_summary = _role_summary(bundle, reserve.assignments, CAL_ROLES)
    _assert_summary(cal_summary, EXPECTED_CAL_SUMMARY, "cal_reserve")
    regime_ii = _regime_ii(bundle, primary, reserve, input_contract)
    population = _population(regime_i, regime_ii)
    report = _report_bytes(primary, reserve, role_summary, population)

    rendered_without_manifest = {
        output_paths["regime_i"]: _json_bytes(regime_i),
        output_paths["regime_ii"]: _json_bytes(regime_ii),
        output_paths["population"]: _yaml_bytes(population),
        output_paths["report"]: report,
    }
    artifact_hashes = {
        path.relative_to(safe_root).as_posix(): sha256_bytes(content)
        for path, content in rendered_without_manifest.items()
    }
    manifest = {
        "schema_version": 1,
        "artifact": "NC_HSG_JOINT_SPLIT_MANIFEST_V1",
        "policy_id": SPLIT_POLICY_ID,
        "population_policy_id": POPULATION_POLICY_ID,
        "inputs": input_contract,
        "primary_assignment": {
            "domain_hex": PRIMARY_DOMAIN.hex(), "role_order": list(PRIMARY_ROLES),
            "capacities": list(PRIMARY_CAPACITIES), "objective_definition": [
                "max_subject_integer_deviation", "sum_subject_integer_deviation_squared",
                "max_block_integer_deviation", "sum_block_integer_deviation_squared",
                "max_occurrence_integer_deviation", "sum_occurrence_integer_deviation_squared",
            ],
            "iterations": primary.iterations, "objective": list(primary.objective),
            "initial_order_sha256": primary.initial_order_sha256,
            "ledger_sha256": primary.ledger_sha256,
        },
        "calibration_reserve_assignment": {
            "domain_hex": CAL_DOMAIN.hex(), "role_order": list(CAL_ROLES),
            "capacities": list(CAL_CAPACITIES), "iterations": reserve.iterations,
            "objective": list(reserve.objective), "initial_order_sha256": reserve.initial_order_sha256,
            "ledger_sha256": reserve.ledger_sha256,
        },
        "role_summary": role_summary,
        "calibration_reserve_summary": cal_summary,
        "regime_ii": {
            "folds": 18, "interpretation": "EMPIRICAL_EXTERNAL_VALIDITY_ONLY",
            "canonical_rows_per_fold": 5905,
        },
        "bootstrap_index_bytes_sha256": population["paired_subject_bootstrap"]["index_bytes_sha256"],
        "artifact_hashes": artifact_hashes,
        "assertions": {
            "groups_covered_once": True, "exact_ids_covered_once": True,
            "stimulus_occurrences_covered_once": True, "analysis_rows_covered_once": True,
            "role_group_sets_pairwise_disjoint": True, "all_subjects_present_in_each_regime_i_role": True,
            "regime_ii_subject_and_group_leakage": False,
            "test_status": "LOCKED_UNTIL_ROUTE_LOCK",
        },
        "safety": {
            "allowed_analysis_fields_only": True, "raw_assignment_metadata_projected": False,
            "random_assignment_generated": False, "test_values_read": False,
            "scientific_statistics_computed": False, "backbone_selected": False,
            "full_leakage_audit_executed": False, "training_executed": False,
            "gate_executed": False,
        },
    }
    rendered = dict(rendered_without_manifest)
    rendered[output_paths["manifest"]] = _yaml_bytes(manifest)
    _atomic_write(rendered)
    return {
        "primary": primary, "reserve": reserve, "regime_i": regime_i,
        "regime_ii": regime_ii, "population": population, "manifest": manifest,
        "output_sha256": {
            path.relative_to(safe_root).as_posix(): sha256_bytes(content)
            for path, content in rendered.items()
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path)
    args = parser.parse_args(argv)
    try:
        result = build(output_root=args.output_root)
    except JointSplitError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    for name, digest in sorted(result["output_sha256"].items()):
        print(f"{name} {digest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
