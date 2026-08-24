"""Metadata-only implementation of the frozen N1 joint permutation law."""

from __future__ import annotations

import hashlib
import json
import struct
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping


ASSIGNMENT_RELATIVE = "artifacts/nulls/n1_block_assignment_v1.jsonl"
ASSIGNMENT_SHA256 = "d0acc5e5fe78bc36a69cb04b6f605983c675e49a764538ae1665f86a28acee04"
POLICY_ID = "RC_HSG_N1_JOINT_PERMUTATION_SAMPLER_V1"
REPLICATES = 199
EXPECTED_ROWS = 3541
EXPECTED_EVALUABLE_ROWS = 3481
EXPECTED_EVALUABLE_BLOCKS = 180
EXPECTED_EXCLUSIONS = 60
PERMUTATION_PREFIX = b"RC_HSG_N1_FEASIBILITY_V1\0PERM\0"
LEDGER_FIELDS = (
    "subject", "session", "slot", "occurrence_id", "role", "raw_samples", "window_count",
    "a_interface_status", "action", "length_bin", "power_bin", "power_edge_cell_id",
    "power_edge_status", "block_id", "block_size", "n1_evaluable", "n1_status",
    "source_file", "source_field", "source_dataset_read_run017",
)
EVALUABLE_STATUS = "N1_EVALUABLE"
EXCLUSION_COUNTS = {
    "N1_NOT_EVALUABLE_SHORT_FORCED_L0": 44,
    "N1_NOT_EVALUABLE_POWER_EDGE_UNAVAILABLE": 4,
    "N1_NOT_EVALUABLE_SINGLETON": 12,
}
OUTER_ROLES = {"train_fit", "inner_val"}
LENGTH_BINS = {"W01_04", "W05_16", "W17_PLUS"}
POWER_BINS = {"P_LOW", "P_HIGH"}


class N1SamplerContractError(RuntimeError):
    """Raised when frozen N1 sampler input or scope checks fail."""


@dataclass(frozen=True)
class N1PermutationPair:
    recipient_row_key: str
    donor_row_key: str
    block_id: str
    fixed_point: bool


@dataclass(frozen=True)
class N1PermutationBatch:
    replicate_id: int
    pairs: tuple[N1PermutationPair, ...]
    excluded_row_keys: tuple[str, ...]
    joint_mapping_sha256: str
    fixed_points: int


@dataclass(frozen=True)
class N1SelectionAwareEvaluation:
    replicate_id: int | None
    evaluations: tuple[tuple[str, Any], ...]
    excluded_row_keys: tuple[str, ...]
    joint_mapping_sha256: str | None


@dataclass(frozen=True)
class _AssignmentRow:
    row_key: str
    block_id: str | None
    evaluable: bool
    role: str
    subject: str
    session: int
    length_bin: str
    power_bin: str | None
    status: str
    block_size: int


def _fail(code: str, detail: str) -> None:
    raise N1SamplerContractError(f"{code}: {detail}")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
    except OSError as exc:
        _fail("N1_SAMPLER_INPUT_MISMATCH", f"assignment-read:{type(exc).__name__}")
    return digest.hexdigest()


def _reject_symlink_chain(path: Path, stop: Path, label: str) -> None:
    current = path.absolute()
    stop = stop.absolute()
    while True:
        if current.is_symlink():
            _fail("N1_SAMPLER_INPUT_MISMATCH", f"symlink:{label}")
        if current == stop or current.parent == current:
            return
        current = current.parent


def _assignment_path(project_root: Path) -> Path:
    root = project_root.absolute()
    _reject_symlink_chain(root, Path(root.anchor), "project-root")
    if not root.is_dir():
        _fail("N1_SAMPLER_INPUT_MISMATCH", "project-root-type")
    relative = Path(ASSIGNMENT_RELATIVE)
    if relative.is_absolute() or ".." in relative.parts:
        _fail("N1_SAMPLER_INPUT_MISMATCH", "assignment-path")
    candidate = root / relative
    _reject_symlink_chain(candidate, root, "assignment")
    try:
        resolved_root = root.resolve(strict=True)
        resolved = candidate.resolve(strict=True)
        resolved.relative_to(resolved_root)
    except (OSError, ValueError):
        _fail("N1_SAMPLER_INPUT_MISMATCH", "assignment-escape-or-missing")
    if not resolved.is_file() or resolved.suffix.lower() != ".jsonl":
        _fail("N1_SAMPLER_INPUT_MISMATCH", "assignment-type")
    if _sha256(resolved) != ASSIGNMENT_SHA256:
        _fail("N1_SAMPLER_INPUT_MISMATCH", "assignment-hash")
    return resolved


def _ascii(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value or "\t" in value or "\n" in value or "\r" in value:
        _fail("N1_SAMPLER_SCOPE_MISMATCH", label)
    try:
        value.encode("ascii")
    except UnicodeEncodeError:
        _fail("N1_SAMPLER_SCOPE_MISMATCH", label)
    return value


def _canonical_row_key(row: dict[str, Any]) -> str:
    subject = _ascii(row.get("subject"), "subject")
    occurrence = _ascii(row.get("occurrence_id"), "occurrence-id")
    slot = row.get("slot")
    if not isinstance(slot, int) or isinstance(slot, bool) or not 0 <= slot <= 999999:
        _fail("N1_SAMPLER_SCOPE_MISMATCH", "slot")
    return f"{subject}\t{slot:06d}\t{occurrence}"


def _expected_block_id(row: dict[str, Any]) -> str:
    payload = (
        f"{row['role']}\t{row['subject']}\t{row['session']}\t"
        f"{row['length_bin']}\t{row['power_bin']}"
    ).encode("ascii")
    return "n1b_v1_" + hashlib.sha256(b"RC_HSG_N1_BLOCK_V1\0" + payload).hexdigest()


def _validate_common(row: dict[str, Any], row_key: str) -> None:
    if tuple(row) != LEDGER_FIELDS:
        _fail("N1_SAMPLER_INPUT_MISMATCH", f"schema:{row_key}")
    if row.get("role") not in OUTER_ROLES:
        _fail("N1_SAMPLER_SCOPE_MISMATCH", f"role:{row_key}")
    if row.get("session") != 1:
        _fail("N1_SAMPLER_SCOPE_MISMATCH", f"session:{row_key}")
    if row.get("source_field") != "rawData":
        _fail("N1_SAMPLER_SCOPE_MISMATCH", f"source-field:{row_key}")
    for field in ("raw_samples", "window_count", "block_size"):
        value = row.get(field)
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            _fail("N1_SAMPLER_SCOPE_MISMATCH", f"{field}:{row_key}")


def _parse_row(row: dict[str, Any]) -> _AssignmentRow:
    row_key = _canonical_row_key(row)
    _validate_common(row, row_key)
    status = row.get("n1_status")
    evaluable = row.get("n1_evaluable")
    if not isinstance(evaluable, bool) or not isinstance(status, str):
        _fail("N1_SAMPLER_SCOPE_MISMATCH", f"status:{row_key}")
    block_id = row.get("block_id")
    power_bin = row.get("power_bin")
    length_bin = row.get("length_bin")

    if evaluable or status == "N1_NOT_EVALUABLE_SINGLETON":
        if row.get("a_interface_status") != "ELIGIBLE" or row.get("action") != "RUN_FRONTEND":
            _fail("N1_SAMPLER_SCOPE_MISMATCH", f"eligibility:{row_key}")
        if row.get("source_dataset_read_run017") is not True:
            _fail("N1_SAMPLER_SCOPE_MISMATCH", f"read-flag:{row_key}")
        if length_bin not in LENGTH_BINS or power_bin not in POWER_BINS:
            _fail("N1_SAMPLER_SCOPE_MISMATCH", f"bin:{row_key}")
        if not isinstance(block_id, str) or block_id != _expected_block_id(row):
            _fail("N1_SAMPLER_SCOPE_MISMATCH", f"block-id:{row_key}")
        expected_size = 1 if status == "N1_NOT_EVALUABLE_SINGLETON" else None
        if evaluable and (status != EVALUABLE_STATUS or row["block_size"] < 2):
            _fail("N1_SAMPLER_SCOPE_MISMATCH", f"evaluable:{row_key}")
        if not evaluable and (expected_size != row["block_size"]):
            _fail("N1_SAMPLER_SCOPE_MISMATCH", f"singleton:{row_key}")
    elif status == "N1_NOT_EVALUABLE_SHORT_FORCED_L0":
        if (
            row.get("a_interface_status") != "A_INTERFACE_SHORT_SEGMENT"
            or row.get("action") != "FORCED_L0_NO_FRONTEND"
            or row.get("source_dataset_read_run017") is not False
            or length_bin != "NOT_APPLICABLE_SHORT"
            or power_bin is not None
            or block_id is not None
            or row["block_size"] != 0
        ):
            _fail("N1_SAMPLER_SCOPE_MISMATCH", f"short:{row_key}")
    elif status == "N1_NOT_EVALUABLE_POWER_EDGE_UNAVAILABLE":
        if (
            row.get("a_interface_status") != "ELIGIBLE"
            or row.get("action") != "RUN_FRONTEND"
            or row.get("source_dataset_read_run017") is not True
            or length_bin not in LENGTH_BINS
            or power_bin is not None
            or block_id is not None
            or row["block_size"] != 0
            or row.get("power_edge_status") != "INSUFFICIENT_TRAIN_CELL"
        ):
            _fail("N1_SAMPLER_SCOPE_MISMATCH", f"edge:{row_key}")
    else:
        _fail("N1_SAMPLER_SCOPE_MISMATCH", f"status:{row_key}")

    return _AssignmentRow(
        row_key=row_key,
        block_id=block_id,
        evaluable=evaluable,
        role=row["role"],
        subject=row["subject"],
        session=row["session"],
        length_bin=length_bin,
        power_bin=power_bin,
        status=status,
        block_size=row["block_size"],
    )


def _load_assignment(path: Path) -> tuple[tuple[_AssignmentRow, ...], dict[str, tuple[str, ...]]]:
    parsed: list[_AssignmentRow] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
        for line_number, line in enumerate(lines, start=1):
            value = json.loads(line)
            if not isinstance(value, dict):
                _fail("N1_SAMPLER_INPUT_MISMATCH", f"json-object:{line_number}")
            parsed.append(_parse_row(value))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        _fail("N1_SAMPLER_INPUT_MISMATCH", f"jsonl:{type(exc).__name__}")

    if len(parsed) != EXPECTED_ROWS:
        _fail("N1_SAMPLER_SCOPE_MISMATCH", "row-count")
    row_keys = [row.row_key for row in parsed]
    if row_keys != sorted(row_keys) or len(set(row_keys)) != EXPECTED_ROWS:
        _fail("N1_SAMPLER_SCOPE_MISMATCH", "canonical-row-keys")
    evaluable = [row for row in parsed if row.evaluable]
    excluded = [row for row in parsed if not row.evaluable]
    if len(evaluable) != EXPECTED_EVALUABLE_ROWS or len(excluded) != EXPECTED_EXCLUSIONS:
        _fail("N1_SAMPLER_SCOPE_MISMATCH", "evaluable-exclusion-count")
    if Counter(row.status for row in excluded) != EXCLUSION_COUNTS:
        _fail("N1_SAMPLER_SCOPE_MISMATCH", "exclusion-status-counts")

    grouped: dict[str, list[_AssignmentRow]] = defaultdict(list)
    for row in evaluable:
        assert row.block_id is not None
        grouped[row.block_id].append(row)
    if len(grouped) != EXPECTED_EVALUABLE_BLOCKS:
        _fail("N1_SAMPLER_SCOPE_MISMATCH", "evaluable-block-count")
    blocks: dict[str, tuple[str, ...]] = {}
    for block_id, members in grouped.items():
        scope = {(r.role, r.subject, r.session, r.length_bin, r.power_bin) for r in members}
        if len(scope) != 1 or len(members) < 2:
            _fail("N1_SAMPLER_SCOPE_MISMATCH", f"block-scope:{block_id}")
        if any(row.block_size != len(members) for row in members):
            _fail("N1_SAMPLER_SCOPE_MISMATCH", f"block-size:{block_id}")
        blocks[block_id] = tuple(sorted(row.row_key for row in members))
    return tuple(parsed), blocks


def _validate_replicate(replicate_id: int) -> None:
    if (
        not isinstance(replicate_id, int)
        or isinstance(replicate_id, bool)
        or not 1 <= replicate_id <= REPLICATES
    ):
        _fail("N1_SAMPLER_REPLICATE_INVALID", "replicate")


class N1JointPermutationSampler:
    """Reconstruct the frozen N1 index mapping from committed metadata."""

    def __init__(self, rows: tuple[_AssignmentRow, ...], blocks: dict[str, tuple[str, ...]]):
        self._rows = rows
        self._blocks = dict(blocks)
        self._row_by_key = {row.row_key: row for row in rows}
        self._evaluable_row_keys = tuple(row.row_key for row in rows if row.evaluable)
        self._evaluable_key_set = frozenset(self._evaluable_row_keys)
        self._excluded_row_keys = tuple(row.row_key for row in rows if not row.evaluable)

    @classmethod
    def from_frozen_assignment(cls, project_root: Path) -> "N1JointPermutationSampler":
        path = _assignment_path(Path(project_root))
        rows, blocks = _load_assignment(path)
        return cls(rows, blocks)

    def build(self, replicate_id: int) -> N1PermutationBatch:
        _validate_replicate(replicate_id)
        encoded_replicate = struct.pack(">H", replicate_id)
        pairs: list[N1PermutationPair] = []
        lines: list[bytes] = []
        for block_id in sorted(self._blocks):
            recipients = self._blocks[block_id]
            encoded_block = block_id.encode("ascii")
            donors = sorted(
                recipients,
                key=lambda donor: (
                    hashlib.sha256(
                        PERMUTATION_PREFIX
                        + encoded_replicate
                        + b"\0"
                        + encoded_block
                        + b"\0"
                        + donor.encode("ascii")
                    ).digest(),
                    donor.encode("ascii"),
                ),
            )
            for recipient, donor in zip(recipients, donors, strict=True):
                fixed = recipient == donor
                pairs.append(N1PermutationPair(recipient, donor, block_id, fixed))
                lines.append(
                    f"{replicate_id}\t{block_id}\t{recipient}\t{donor}\n".encode("ascii")
                )
        if len(pairs) != EXPECTED_EVALUABLE_ROWS:
            _fail("N1_SAMPLER_SCOPE_MISMATCH", f"pair-count:{replicate_id}")
        recipient_keys = {pair.recipient_row_key for pair in pairs}
        donor_keys = {pair.donor_row_key for pair in pairs}
        if recipient_keys != self._evaluable_key_set or donor_keys != self._evaluable_key_set:
            _fail("N1_SAMPLER_SCOPE_MISMATCH", f"bijection:{replicate_id}")
        joint_hash = hashlib.sha256(b"".join(sorted(lines))).hexdigest()
        return N1PermutationBatch(
            replicate_id=replicate_id,
            pairs=tuple(pairs),
            excluded_row_keys=self._excluded_row_keys,
            joint_mapping_sha256=joint_hash,
            fixed_points=sum(pair.fixed_point for pair in pairs),
        )

    def donor_for(self, row_key: str, replicate_id: int) -> str:
        _validate_replicate(replicate_id)
        if row_key not in self._row_by_key:
            _fail("N1_SAMPLER_ROW_UNKNOWN", str(row_key))
        if row_key not in self._evaluable_key_set:
            _fail("N1_SAMPLER_ROW_NOT_EVALUABLE", row_key)
        for pair in self.build(replicate_id).pairs:
            if pair.recipient_row_key == row_key:
                return pair.donor_row_key
        _fail("N1_SAMPLER_SCOPE_MISMATCH", f"mapping:{replicate_id}")

    def _validate_values(self, values_by_row: Mapping[str, Any]) -> None:
        if not isinstance(values_by_row, Mapping):
            _fail("N1_SAMPLER_VALUE_SCOPE_MISMATCH", "mapping")
        try:
            keys = frozenset(values_by_row.keys())
        except Exception:
            _fail("N1_SAMPLER_VALUE_SCOPE_MISMATCH", "keys")
        if keys != self._evaluable_key_set:
            _fail("N1_SAMPLER_VALUE_SCOPE_MISMATCH", "key-set")

    def _evaluate(
        self,
        replicate_id: int | None,
        values_by_row: Mapping[str, Any],
        select_then_score: Callable[[str, str, Any], Any],
    ) -> N1SelectionAwareEvaluation:
        self._validate_values(values_by_row)
        if not callable(select_then_score):
            _fail("N1_SAMPLER_CALLBACK_FAILURE", "not-callable")
        if replicate_id is None:
            donor_by_recipient = {key: key for key in self._evaluable_row_keys}
            joint_hash = None
        else:
            batch = self.build(replicate_id)
            donor_by_recipient = {
                pair.recipient_row_key: pair.donor_row_key for pair in batch.pairs
            }
            joint_hash = batch.joint_mapping_sha256
        evaluations: list[tuple[str, Any]] = []
        for recipient in self._evaluable_row_keys:
            donor = donor_by_recipient[recipient]
            try:
                value = values_by_row[donor]
                result = select_then_score(recipient, donor, value)
            except Exception:
                label = "real" if replicate_id is None else str(replicate_id)
                _fail("N1_SAMPLER_CALLBACK_FAILURE", f"{label}:{recipient}")
            evaluations.append((recipient, result))
        return N1SelectionAwareEvaluation(
            replicate_id=replicate_id,
            evaluations=tuple(evaluations),
            excluded_row_keys=self._excluded_row_keys,
            joint_mapping_sha256=joint_hash,
        )

    def evaluate_real(
        self,
        values_by_row: Mapping[str, Any],
        select_then_score: Callable[[str, str, Any], Any],
    ) -> N1SelectionAwareEvaluation:
        return self._evaluate(None, values_by_row, select_then_score)

    def evaluate_pseudo_real(
        self,
        replicate_id: int,
        values_by_row: Mapping[str, Any],
        select_then_score: Callable[[str, str, Any], Any],
    ) -> N1SelectionAwareEvaluation:
        _validate_replicate(replicate_id)
        return self._evaluate(replicate_id, values_by_row, select_then_score)
