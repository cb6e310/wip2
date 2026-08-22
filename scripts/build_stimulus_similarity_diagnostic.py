#!/usr/bin/env python3
"""Bind ZuCo NR stimulus sources and build a text-free similarity diagnostic."""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.metadata
import json
import math
import os
import platform
import re
import sys
import tempfile
import unicodedata
from collections import Counter, defaultdict
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_EVEN
from pathlib import Path
from typing import Any, Iterable, Protocol, Sequence

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODEL_REPO_ID = "sentence-transformers/all-MiniLM-L6-v2"
MODEL_REVISION = "c9745ed1d9f207416be6d2e6f8de32d1f16199bf"
MODEL_LICENSE = "Apache-2.0"
MODEL_DIMENSION = 384
MODEL_FILE_SHA256 = {
    "1_Pooling/config.json": "4be450dde3b0273bb9787637cfbd28fe04a7ba6ab9d36ac48e92b11e350ffc23",
    "README.md": "7dfc82496ec33f906b5b0d6750c1e2397da6530c74d1ae3568c55bc2739125e7",
    "config.json": "953f9c0d463486b10a6871cc2fd59f223b2c70184f49815e7efbcab5d8908b41",
    "config_sentence_transformers.json": "061ca9d39661d6c6d6de5ba27f79a1cd5770ea247f8d46412a68a498dc5ac9f3",
    "model.safetensors": "53aa51172d142c89d9012cce15ae4d6cc0ca6895895114379cacb4fab128d9db",
    "modules.json": "84e40c8e006c9b1d6c122e02cba9b02458120b5fb0c87b746c41e0207cf642cf",
    "sentence_bert_config.json": "fc1993fde0a95c24ec6c022539d41cf6e2f7c9721e5415d6fb6897472a9cd4b7",
    "special_tokens_map.json": "303df45a03609e4ead04bc3dc1536d0ab19b5358db685b6f3da123d05ec200e3",
    "tokenizer.json": "be50c3628f2bf5bb5e3a7f17b1f74611b2561a3a27eeab05e5aa30f411572037",
    "tokenizer_config.json": "acb92769e8195aabd29b7b2137a9e6d6e25c476a4f15aa4355c233426c61576b",
    "vocab.txt": "07eced375cec144d27c900241f3e339478dec958f92fddbc551f295c992038a3",
}
CSV_SHA256 = {
    "nr_1.csv": "77291d9fe66797781efa7c093824a16198f38e92ac34067e8bf20d76d5c50386",
    "nr_2.csv": "68a6885dd96d4fa386297d7f30352c2077b565577c68dcb2205b19d506042132",
    "nr_3.csv": "1a1ead3a1dfa12d8ff73dbe619db94b6ce202b35a3d19358d67f01c3115553ba",
    "nr_4.csv": "d7b5c9b3a0e6d55958b976b0ea2cc6c236720ead947d6851d15de798e712965f",
    "nr_5.csv": "2ca84d88f3267ecc4686f357cc97f2c077a2b90534ecbc8615b2197e2f93b5bc",
    "nr_6.csv": "3722ba205f8b63e801791ef3303dcdbf52bbef3c6bd157bd11a16ccd40e1861a",
    "nr_7.csv": "575a938092ca1db20d883fed180cb48fa66deca53097267874fe784fdc44cf9b",
}
COMMITTED_INPUT_SHA256 = {
    "targeted_manifest": "50806a60937b28ae36207509c44d606af6f6b6b1be2a69c06081672f0931bfaf",
    "stimulus_manifest": "2512c55bb7471896aad7bfa7ba96843fbce8a46067abffda6c16ad87ce3e44be",
    "analysis_view": "0751259f9f9455cba72bd7d027ffa1423e790e631ac0f5174c38da65d7cd12ff",
    "analysis_summary": "5e387ef3dc9e930e3ca3e4b6ccb6a009a3cc719281f1ac183cfbf56ac7b66181",
    "data_card": "d9331bfe34937c264b7b8c667a2b831569c4440120e1d445011aeaf419c30f84",
}
COMMITTED_BASENAMES = {
    "targeted_manifest": "zuco2_nr_targeted_manifest_v3.yaml",
    "stimulus_manifest": "zuco2_nr_stimulus_manifest_v3.jsonl",
    "analysis_view": "zuco2_nr_analysis_view_v1.jsonl",
    "analysis_summary": "zuco2_nr_analysis_view_v1.yaml",
    "data_card": "data_card.yaml",
}
CANDIDATE_FIELDS = (
    "id_a", "id_b", "edit_similarity", "token_jaccard", "embedding_cosine",
    "trigger_edit_080", "trigger_jaccard_070", "trigger_embedding_070",
    "length_chars_a", "length_chars_b", "slots_a", "slots_b",
)
QUANTILES = (0.0, 0.01, 0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95, 0.99, 1.0)
COMPONENT_CUTS = {
    "edit_similarity": (0.80, 0.85, 0.90, 0.95),
    "token_jaccard": (0.70, 0.80, 0.90),
    "embedding_cosine": (0.70, 0.75, 0.80, 0.85, 0.90),
}


class DiagnosticError(RuntimeError):
    def __init__(self, code: str, detail: str):
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}")


def _fail(code: str, detail: str) -> None:
    raise DiagnosticError(code, detail)


@dataclass(frozen=True)
class Expectations:
    material_rows: int = 370
    practice_rows: int = 21
    task_slots: int = 349
    per_block_slots: tuple[int, ...] = (50, 50, 51, 50, 50, 49, 49)
    unique_identities: int = 344
    exact_duplicate_groups: int = 5
    analysis_view_rows: int = 5905
    stimulus_subjects: int = 18
    model_dimension: int = MODEL_DIMENSION
    max_wordpieces: int = 256


DEFAULT_EXPECTATIONS = Expectations()


class EmbeddingBackend(Protocol):
    def embed(
        self, texts: Sequence[str], model_dir: Path, expected_dimension: int,
    ) -> tuple[list[list[float]], list[int], dict[str, str]]: ...


class SafeTransformerBackend:
    def embed(
        self, texts: Sequence[str], model_dir: Path, expected_dimension: int,
    ) -> tuple[list[list[float]], list[int], dict[str, str]]:
        try:
            import torch
            import torch.nn.functional as functional
            from transformers import AutoModel, AutoTokenizer
        except ImportError as exc:
            _fail("FROZEN_EMBEDDING_MODEL_UNAVAILABLE", type(exc).__name__)
        tokenizer = AutoTokenizer.from_pretrained(
            str(model_dir), local_files_only=True, trust_remote_code=False,
        )
        probe = tokenizer(list(texts), add_special_tokens=True, padding=False, truncation=False)
        token_counts = [len(values) for values in probe["input_ids"]]
        model = AutoModel.from_pretrained(
            str(model_dir), local_files_only=True, trust_remote_code=False,
            use_safetensors=True,
        )
        model.to("cpu")
        model.eval()
        vectors: list[list[float]] = []
        with torch.no_grad():
            for start in range(0, len(texts), 16):
                encoded = tokenizer(
                    list(texts[start:start + 16]), padding=True, truncation=False,
                    return_tensors="pt",
                )
                encoded = {key: value.to("cpu") for key, value in encoded.items()}
                output = model(**encoded).last_hidden_state
                mask = encoded["attention_mask"].unsqueeze(-1).expand(output.size()).float()
                pooled = (output * mask).sum(1) / mask.sum(1).clamp(min=1e-9)
                pooled = functional.normalize(pooled.float(), p=2, dim=1)
                if pooled.shape[1] != expected_dimension:
                    _fail("MODEL_DIMENSION_MISMATCH", str(pooled.shape[1]))
                vectors.extend(pooled.cpu().tolist())
        versions = {
            "python": platform.python_version(),
            "torch": importlib.metadata.version("torch"),
            "transformers": importlib.metadata.version("transformers"),
            "tokenizers": importlib.metadata.version("tokenizers"),
            "safetensors": importlib.metadata.version("safetensors"),
        }
        return vectors, token_counts, versions


def normalize_exact(value: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", value).strip().split())


def normalize_lexical(value: str) -> str:
    exact = normalize_exact(value).casefold()
    return " ".join("".join(char if char.isalnum() else " " for char in exact).split())


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def levenshtein_distance(left: str, right: str) -> int:
    """Exact Myers bit-vector Levenshtein distance for arbitrary-length strings."""
    if len(left) > len(right):
        left, right = right, left
    if not left:
        return len(right)
    masks: dict[str, int] = {}
    for index, char in enumerate(left):
        masks[char] = masks.get(char, 0) | (1 << index)
    positive = ~0
    negative = 0
    score = len(left)
    highest = 1 << (len(left) - 1)
    for char in right:
        equal = masks.get(char, 0)
        vertical = equal | negative
        horizontal = (((equal & positive) + positive) ^ positive) | equal
        positive_horizontal = negative | ~(horizontal | positive)
        negative_horizontal = positive & horizontal
        if positive_horizontal & highest:
            score += 1
        elif negative_horizontal & highest:
            score -= 1
        positive_horizontal = (positive_horizontal << 1) | 1
        negative_horizontal <<= 1
        positive = negative_horizontal | ~(vertical | positive_horizontal)
        negative = positive_horizontal & vertical
    return score


def edit_similarity(left: str, right: str) -> float:
    denominator = max(len(left), len(right))
    if denominator == 0:
        _fail("EMPTY_LEXICAL_STRING", "edit similarity")
    return 1.0 - levenshtein_distance(left, right) / denominator


def token_jaccard(left: Sequence[str], right: Sequence[str]) -> float:
    left_set, right_set = set(left), set(right)
    union = left_set | right_set
    if not union:
        _fail("EMPTY_TOKEN_UNION", "token Jaccard")
    return len(left_set & right_set) / len(union)


def cosine(left: Sequence[float], right: Sequence[float]) -> float:
    if len(left) != len(right) or not left:
        _fail("EMBEDDING_DIMENSION_MISMATCH", "cosine")
    return sum(a * b for a, b in zip(left, right))


def round_half_even(value: float, digits: int = 6) -> float:
    quantum = Decimal(1).scaleb(-digits)
    rounded = Decimal(str(value)).quantize(quantum, rounding=ROUND_HALF_EVEN)
    result = float(rounded)
    return 0.0 if result == 0 else result


def unordered_pair_count(items: int) -> int:
    return items * (items - 1) // 2


def _safe_input(path: Path, root: Path, label: str, basename: str | None = None) -> Path:
    root = root.resolve()
    candidate = path if path.is_absolute() else root / path
    current = candidate
    while True:
        if current.is_symlink():
            _fail("INPUT_SYMLINK", label)
        if current == root or current.parent == current:
            break
        current = current.parent
    resolved = candidate.resolve()
    try:
        resolved.relative_to(root)
    except ValueError:
        _fail("INPUT_PATH_ESCAPE", label)
    if not resolved.is_file():
        _fail("INPUT_NOT_FILE", label)
    if basename is not None and resolved.name != basename:
        _fail("INPUT_BASENAME_MISMATCH", label)
    return resolved


def _safe_output(path: Path, root: Path, label: str) -> Path:
    root = root.resolve()
    candidate = path if path.is_absolute() else root / path
    if candidate.exists() and candidate.is_symlink():
        _fail("OUTPUT_SYMLINK", label)
    parent = candidate.parent.resolve()
    try:
        parent.relative_to(root)
    except ValueError:
        _fail("OUTPUT_PATH_ESCAPE", label)
    return parent / candidate.name


def _load_yaml(path: Path, label: str) -> dict[str, Any]:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        _fail("INPUT_PARSE_ERROR", f"{label}:{type(exc).__name__}")
    if not isinstance(value, dict):
        _fail("INPUT_SCHEMA_MISMATCH", label)
    return value


def _load_jsonl(path: Path, label: str) -> list[dict[str, Any]]:
    rows = []
    try:
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            value = json.loads(line)
            if not isinstance(value, dict):
                _fail("INPUT_SCHEMA_MISMATCH", f"{label}:{number}")
            rows.append(value)
    except DiagnosticError:
        raise
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        _fail("INPUT_PARSE_ERROR", f"{label}:{type(exc).__name__}")
    return rows


def _validate_model(
    model_dir: Path, expected_revision: str, expected_hashes: dict[str, str],
) -> list[dict[str, Any]]:
    model_dir = model_dir.resolve()
    if not model_dir.is_dir():
        _fail("FROZEN_EMBEDDING_MODEL_UNAVAILABLE", str(model_dir))
    if model_dir.name != expected_revision:
        _fail("MODEL_REVISION_MISMATCH", model_dir.name)
    cache_root = model_dir.parent.parent.resolve()
    discovered: set[str] = set()
    for directory, _, files in os.walk(model_dir, followlinks=False):
        for name in files:
            path = Path(directory) / name
            relative = path.relative_to(model_dir).as_posix()
            discovered.add(relative)
            try:
                path.resolve().relative_to(cache_root)
            except ValueError:
                _fail("MODEL_PATH_ESCAPE", relative)
            if path.suffix.lower() in {".bin", ".pkl", ".pickle", ".onnx", ".h5", ".pb", ".msgpack"}:
                _fail("UNSAFE_MODEL_FILE", relative)
    if "model.safetensors" not in discovered:
        _fail("MODEL_SAFETENSORS_MISSING", "model.safetensors")
    if discovered != set(expected_hashes):
        _fail("MODEL_FILE_ALLOWLIST_MISMATCH", repr(sorted(discovered ^ set(expected_hashes))))
    inventory = []
    for relative in sorted(expected_hashes):
        path = model_dir / relative
        digest = sha256_file(path)
        if digest != expected_hashes[relative]:
            _fail("MODEL_FILE_HASH_MISMATCH", relative)
        inventory.append({"path": relative, "size_bytes": path.stat().st_size, "sha256": digest})
    return inventory


def _read_materials(
    dataset_root: Path,
    expected_hashes: dict[str, str],
    enforce_dataset_basename: bool,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[str, str]]:
    if dataset_root.is_symlink():
        _fail("INPUT_SYMLINK", "dataset_root")
    root = dataset_root.resolve()
    if not root.is_dir() or (enforce_dataset_basename and root.name != "zuco_2.0"):
        _fail("DATASET_ROOT_INVALID", str(root))
    all_rows: list[dict[str, Any]] = []
    practice: list[dict[str, Any]] = []
    task_rows: list[dict[str, Any]] = []
    hashes: dict[str, str] = {}
    for block in range(1, len(expected_hashes) + 1):
        name = f"nr_{block}.csv"
        if name not in expected_hashes:
            _fail("SOURCE_FILE_ALLOWLIST_MISMATCH", name)
        path = root / "task_materials" / name
        if path.is_symlink():
            _fail("INPUT_SYMLINK", name)
        resolved = path.resolve()
        try:
            resolved.relative_to(root)
        except ValueError:
            _fail("INPUT_PATH_ESCAPE", name)
        digest = sha256_file(resolved)
        hashes[name] = digest
        if digest != expected_hashes[name]:
            _fail("STIMULUS_SOURCE_HASH_MISMATCH", name)
        block_rows = []
        with resolved.open("r", encoding="utf-8-sig", newline="") as handle:
            for material_line, columns in enumerate(csv.reader(handle, delimiter=";"), 1):
                if not columns or not any(value.strip() for value in columns):
                    continue
                if len(columns) < 3:
                    _fail("MATERIAL_ROW_SCHEMA_MISMATCH", f"{name}:{material_line}")
                exact = normalize_exact(columns[2])
                lexical = normalize_lexical(exact)
                if not exact or not lexical:
                    _fail("EMPTY_LEXICAL_STRING", f"{name}:{material_line}")
                record = {
                    "block": block,
                    "material_line": material_line,
                    "exact": exact,
                    "lexical": lexical,
                    "tokens": tuple(lexical.split(" ")),
                    "exact_stimulus_id": sha256_text(exact),
                    "lexical_sha256": sha256_text(lexical),
                    "length_chars": len(exact),
                    "practice": len(block_rows) < 3,
                }
                block_rows.append(record)
                all_rows.append(record)
                (practice if record["practice"] else task_rows).append(record)
    for slot, row in enumerate(task_rows, 1):
        row["slot"] = slot
    return all_rows, practice, task_rows, hashes


def _quantile(sorted_values: Sequence[float], probability: float) -> float:
    if not sorted_values:
        _fail("PAIR_COUNT_MISMATCH", "empty score distribution")
    position = (len(sorted_values) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return sorted_values[lower]
    fraction = position - lower
    return sorted_values[lower] * (1 - fraction) + sorted_values[upper] * fraction


def _distribution(values: Sequence[float], lower: float, upper: float) -> dict[str, Any]:
    sorted_values = sorted(values)
    width = 0.01
    bins = int(round((upper - lower) / width))
    counts = [0] * bins
    for value in values:
        index = math.floor((value - lower) / width)
        counts[max(0, min(bins - 1, index))] += 1
    histogram = []
    for index, count in enumerate(counts):
        start = Decimal(str(lower)) + Decimal("0.01") * index
        end = start + Decimal("0.01")
        histogram.append({"lower": format(start, ".2f"), "upper": format(end, ".2f"), "count": count})
    return {
        "min": round_half_even(sorted_values[0]),
        "max": round_half_even(sorted_values[-1]),
        "quantiles": [
            {"q": format(Decimal(str(probability)), "f"), "value": round_half_even(_quantile(sorted_values, probability))}
            for probability in QUANTILES
        ],
        "histogram_width": 0.01,
        "histogram": histogram,
    }


def _component_summary(ids: Sequence[str], edges: Iterable[tuple[str, str]]) -> dict[str, Any]:
    parent = {identity: identity for identity in ids}
    size = {identity: 1 for identity in ids}

    def find(item: str) -> str:
        while parent[item] != item:
            parent[item] = parent[parent[item]]
            item = parent[item]
        return item

    for left, right in edges:
        left_root, right_root = find(left), find(right)
        if left_root == right_root:
            continue
        if size[left_root] < size[right_root]:
            left_root, right_root = right_root, left_root
        parent[right_root] = left_root
        size[left_root] += size[right_root]
    component_sizes = Counter(find(identity) for identity in ids)
    size_counts = Counter(component_sizes.values())
    return {
        "component_count": len(component_sizes),
        "singleton_components": size_counts[1],
        "non_singleton_components": sum(count for value, count in size_counts.items() if value > 1),
        "largest_component": max(component_sizes.values(), default=0),
        "component_size_counts": {value: size_counts[value] for value in sorted(size_counts)},
        "formal_group_ids_emitted": False,
    }


def _yaml_bytes(value: Any) -> bytes:
    return yaml.safe_dump(value, sort_keys=False, allow_unicode=False).encode("utf-8")


def _jsonl_bytes(rows: Iterable[dict[str, Any]]) -> bytes:
    return b"".join(
        (json.dumps(row, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n").encode("utf-8")
        for row in rows
    )


def _report_bytes(diagnostic: dict[str, Any]) -> bytes:
    counts = diagnostic["counts"]
    model = diagnostic["embedding_model"]
    prefilter = diagnostic["broad_diagnostic_prefilter"]
    lines = [
        "# ZuCo 2.0 NR Stimulus Similarity Diagnostic", "",
        "## Scope", "",
        f"The bounded source binding recovered {counts['material_rows']} material rows, excluded {counts['practice_rows']} practice rows, and bound {counts['task_slots']} task slots to {counts['unique_exact_identities']} opaque exact identities. {counts['exact_duplicate_groups']} exact duplicate groups remain separate from the all-pair diagnostic.", "",
        f"All {counts['unordered_pairs']:,} unordered pairs were scored with normalized edit similarity, token-set Jaccard, and cosine from `{model['repo_id']}@{model['revision']}`. No stimulus sentence, token, n-gram, or embedding vector is present in committed outputs.", "",
        "## Frozen model", "",
        f"- License: `{model['license']}`",
        f"- Dimension: {model['dimension']}",
        f"- Wordpieces including special tokens: min {model['wordpieces']['min']}, max {model['wordpieces']['max']}; no truncation",
        f"- Safe files: {len(model['files'])}, all hash-verified; `model.safetensors` only", "",
        "## Broad diagnostic prefilter", "",
        "The committed candidate ledger uses the preregistered OR rule: edit >= 0.80, token Jaccard >= 0.70, or embedding cosine >= 0.70.", "",
        f"- Candidate union: {prefilter['union_count']}",
        f"- Edit trigger: {prefilter['trigger_counts']['edit_080']}",
        f"- Jaccard trigger: {prefilter['trigger_counts']['jaccard_070']}",
        f"- Embedding trigger: {prefilter['trigger_counts']['embedding_070']}", "",
        "Histograms, registered quantiles, top-1000 opaque pairs, trigger intersections, and single-metric component-risk summaries are recorded in the machine-readable diagnostic.", "",
        "## Decision boundary", "",
        "No final near-duplicate threshold or grouping policy was selected. High similarity is not a verified paraphrase label. Document and paragraph metadata are unavailable from the bound source contract. The next action is ChatGPT/author policy review; Codex must not create groups or splits from this diagnostic.", "",
        "No EEG, event, TSR, outcome, historical result, prediction, checkpoint, or trust_align result tree was read. No A was selected, no training occurred, and no Gate ran.", "",
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
    dataset_root: Path,
    targeted_manifest: Path,
    stimulus_manifest: Path,
    analysis_view: Path,
    analysis_summary: Path,
    data_card: Path,
    model_dir: Path,
    output_source_binding: Path,
    output_diagnostic: Path,
    output_candidates: Path,
    output_report: Path,
    root: Path = PROJECT_ROOT,
    expectations: Expectations = DEFAULT_EXPECTATIONS,
    csv_hashes: dict[str, str] = CSV_SHA256,
    committed_hashes: dict[str, str] | None = None,
    expected_model_hashes: dict[str, str] = MODEL_FILE_SHA256,
    expected_model_revision: str = MODEL_REVISION,
    model_acquisition: str = "REUSED_CACHE",
    embedding_backend: EmbeddingBackend | None = None,
    enforce_basenames: bool = False,
) -> dict[str, Any]:
    input_values = {
        "targeted_manifest": targeted_manifest,
        "stimulus_manifest": stimulus_manifest,
        "analysis_view": analysis_view,
        "analysis_summary": analysis_summary,
        "data_card": data_card,
    }
    inputs = {
        label: _safe_input(path, root, label, COMMITTED_BASENAMES[label] if enforce_basenames else None)
        for label, path in input_values.items()
    }
    outputs = {
        "source_binding": _safe_output(output_source_binding, root, "output_source_binding"),
        "diagnostic": _safe_output(output_diagnostic, root, "output_diagnostic"),
        "candidates": _safe_output(output_candidates, root, "output_candidates"),
        "report": _safe_output(output_report, root, "output_report"),
    }
    if len(set(outputs.values())) != 4:
        _fail("OUTPUT_PATH_DUPLICATE", "outputs")
    input_hashes = {label: sha256_file(path) for label, path in inputs.items()}
    if committed_hashes is not None:
        for label, expected in committed_hashes.items():
            if input_hashes.get(label) != expected:
                _fail("COMMITTED_INPUT_HASH_MISMATCH", label)
    if model_acquisition not in {"DOWNLOADED", "REUSED_CACHE"}:
        _fail("MODEL_ACQUISITION_INVALID", model_acquisition)

    targeted = _load_yaml(inputs["targeted_manifest"], "targeted_manifest")
    stimulus_rows = _load_jsonl(inputs["stimulus_manifest"], "stimulus_manifest")
    view_rows = _load_jsonl(inputs["analysis_view"], "analysis_view")
    analysis = _load_yaml(inputs["analysis_summary"], "analysis_summary")
    card = _load_yaml(inputs["data_card"], "data_card")
    if targeted.get("schema_version") != 3 or targeted.get("counts", {}).get("rows") != len(stimulus_rows):
        _fail("TARGETED_SCHEMA_MISMATCH", "schema or rows")
    if analysis.get("analysis_view_admission", {}).get("status") != "PASS":
        _fail("ANALYSIS_VIEW_NOT_ADMITTED", "summary")
    if card.get("analysis_view", {}).get("status") != "PASS":
        _fail("ANALYSIS_VIEW_NOT_ADMITTED", "data card")

    all_material, practice_rows, task_rows, source_hashes = _read_materials(
        dataset_root, csv_hashes, enforce_basenames,
    )
    per_block = Counter(row["block"] for row in task_rows)
    if (
        len(all_material) != expectations.material_rows
        or len(practice_rows) != expectations.practice_rows
        or len(task_rows) != expectations.task_slots
        or tuple(per_block[block] for block in sorted(per_block)) != expectations.per_block_slots
    ):
        _fail("MATERIAL_COUNT_MISMATCH", f"{len(all_material)}/{len(practice_rows)}/{len(task_rows)}")

    source_by_slot = {row["slot"]: row for row in task_rows}
    slot_hashes: dict[int, str] = {}
    subjects = set()
    for row in stimulus_rows:
        slot, identity = row.get("slot"), row.get("stimulus_sha256")
        subject = row.get("subject")
        if not isinstance(slot, int) or slot not in source_by_slot or not isinstance(subject, str):
            _fail("STIMULUS_ROW_SCHEMA_MISMATCH", repr((subject, slot)))
        subjects.add(subject)
        if source_by_slot[slot]["exact_stimulus_id"] != identity:
            _fail("SLOT_HASH_MISMATCH", repr((subject, slot)))
        if any(row.get(key) != source_by_slot[slot][key] for key in ("block", "material_line")):
            _fail("SLOT_SOURCE_POSITION_MISMATCH", repr((subject, slot)))
        if slot in slot_hashes and slot_hashes[slot] != identity:
            _fail("SLOT_HASH_MISMATCH", f"inconsistent slot {slot}")
        slot_hashes[slot] = identity
        if row.get("stimulus_length_chars") != source_by_slot[slot]["length_chars"]:
            _fail("SLOT_LENGTH_MISMATCH", repr((subject, slot)))
    if len(subjects) != expectations.stimulus_subjects or len(slot_hashes) != expectations.task_slots:
        _fail("STIMULUS_ROW_COUNT_MISMATCH", f"subjects={len(subjects)} slots={len(slot_hashes)}")
    sequence = targeted.get("material_contract", {}).get("sequence")
    if not isinstance(sequence, dict) or (
        sequence.get("result") != "PASS"
        or sequence.get("ordered_exact_match_count") != len(stimulus_rows)
        or sequence.get("ordered_expected_match_count") != len(stimulus_rows)
        or sequence.get("mismatches") != []
    ):
        _fail("TARGETED_MATERIAL_SEQUENCE_MISMATCH", "audit result")

    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in task_rows:
        grouped[row["exact_stimulus_id"]].append(row)
    duplicate_ids = sorted(identity for identity, rows in grouped.items() if len(rows) > 1)
    if len(grouped) != expectations.unique_identities or len(duplicate_ids) != expectations.exact_duplicate_groups:
        _fail("EXACT_IDENTITY_COUNT_MISMATCH", f"{len(grouped)}/{len(duplicate_ids)}")
    committed_groups = targeted.get("material_contract", {}).get("cross_block_duplicate_groups", [])
    if sorted(item.get("stimulus_sha256") for item in committed_groups) != duplicate_ids:
        _fail("EXACT_DUPLICATE_GROUP_MISMATCH", "schema-v3")

    view_counts = Counter(row.get("stimulus_sha256") for row in view_rows)
    if len(view_rows) != expectations.analysis_view_rows:
        _fail("ANALYSIS_VIEW_ROW_MISMATCH", str(len(view_rows)))
    missing = sorted(set(grouped) - set(view_counts))
    if missing:
        _fail("ANALYSIS_VIEW_IDENTITY_MISSING", missing[0])

    identity_records = []
    internal = []
    for identity in sorted(grouped):
        occurrences = sorted(grouped[identity], key=lambda row: row["slot"])
        lexical_values = {row["lexical"] for row in occurrences}
        if len(lexical_values) != 1:
            _fail("EXACT_DUPLICATE_LEXICAL_MISMATCH", identity)
        lexical = next(iter(lexical_values))
        record = {
            "exact_stimulus_id": identity,
            "lexical_sha256": sha256_text(lexical),
            "length_chars": occurrences[0]["length_chars"],
            "slots": [row["slot"] for row in occurrences],
            "blocks": sorted({row["block"] for row in occurrences}),
            "material_lines": [row["material_line"] for row in occurrences],
            "analysis_view_row_count": view_counts[identity],
            "document_id": None,
            "paragraph_id": None,
            "document_status": "SOURCE_METADATA_NOT_AVAILABLE",
            "paragraph_status": "SOURCE_METADATA_NOT_AVAILABLE",
            "near_duplicate_group_status": "PENDING_GROUP_POLICY_REVIEW",
        }
        identity_records.append(record)
        internal.append({**record, "exact": occurrences[0]["exact"], "lexical": lexical, "tokens": occurrences[0]["tokens"]})

    exact_groups = [
        {
            "exact_stimulus_id": identity,
            "slots": [row["slot"] for row in sorted(grouped[identity], key=lambda row: row["slot"])],
            "blocks": sorted({row["block"] for row in grouped[identity]}),
            "material_lines": [row["material_line"] for row in sorted(grouped[identity], key=lambda row: row["slot"])],
            "occurrences_remain_distinct": True,
        }
        for identity in duplicate_ids
    ]
    source_binding = {
        "schema_version": 1,
        "artifact": "ZUCO2_NR_STIMULUS_SOURCE_BINDING_V1",
        "source_files": [
            {"path": f"task_materials/{name}", "sha256": source_hashes[name]}
            for name in sorted(source_hashes)
        ],
        "committed_input_hashes": input_hashes,
        "normalization_contract": {
            "N_exact": "Unicode NFKC; strip; every Unicode whitespace run to one ASCII space",
            "exact_stimulus_id": "SHA256(UTF8(N_exact))",
            "N_lex": "N_exact; Unicode casefold; maximal non-alphanumeric run to one space; collapse and strip",
            "lexical_sha256": "SHA256(UTF8(N_lex))",
            "tokens": "non-empty N_lex items split by ASCII space; tokens are not emitted",
        },
        "counts": {
            "material_rows": len(all_material),
            "practice_rows_excluded": len(practice_rows),
            "post_practice_slots": len(task_rows),
            "slot_hash_matches": len(slot_hashes),
            "unique_exact_identities": len(grouped),
            "exact_duplicate_groups": len(exact_groups),
            "analysis_view_rows": len(view_rows),
            "analysis_view_identities_covered": len(set(view_counts) & set(grouped)),
        },
        "per_block_post_practice_slots": {block: per_block[block] for block in sorted(per_block)},
        "identities": identity_records,
        "exact_duplicate_groups": exact_groups,
        "metadata_availability": {
            "document_id": None,
            "paragraph_id": None,
            "document_status": "SOURCE_METADATA_NOT_AVAILABLE",
            "paragraph_status": "SOURCE_METADATA_NOT_AVAILABLE",
            "block_or_line_inference_performed": False,
            "near_duplicate_group_status": "PENDING_GROUP_POLICY_REVIEW",
        },
        "safety": {
            "stimulus_text_emitted": False,
            "lexical_text_emitted": False,
            "tokens_or_ngrams_emitted": False,
            "eeg_or_event_read": False,
            "outcome_read": False,
        },
    }
    source_binding_bytes = _yaml_bytes(source_binding)
    source_binding_hash = hashlib.sha256(source_binding_bytes).hexdigest()

    model_inventory = _validate_model(model_dir, expected_model_revision, expected_model_hashes)
    backend = embedding_backend or SafeTransformerBackend()
    vectors, token_counts, versions = backend.embed(
        [row["exact"] for row in internal], model_dir.resolve(), expectations.model_dimension,
    )
    if len(vectors) != len(internal) or len(token_counts) != len(internal):
        _fail("EMBEDDING_ROW_COUNT_MISMATCH", f"{len(vectors)}/{len(token_counts)}")
    if any(len(vector) != expectations.model_dimension for vector in vectors):
        _fail("MODEL_DIMENSION_MISMATCH", "backend")
    if max(token_counts, default=0) > expectations.max_wordpieces:
        _fail("STIMULUS_EMBEDDING_TRUNCATION_REQUIRED", str(max(token_counts)))
    for index, vector in enumerate(vectors):
        norm = math.sqrt(sum(value * value for value in vector))
        if not math.isfinite(norm) or abs(norm - 1.0) > 1e-5:
            _fail("EMBEDDING_NOT_L2_NORMALIZED", str(index))

    pairs = []
    candidates = []
    metric_values = {name: [] for name in COMPONENT_CUTS}
    trigger_counts = Counter()
    intersections = Counter()
    for left_index, left in enumerate(internal):
        for right_index in range(left_index + 1, len(internal)):
            right = internal[right_index]
            edit_raw = edit_similarity(left["lexical"], right["lexical"])
            jaccard_raw = token_jaccard(left["tokens"], right["tokens"])
            cosine_raw = cosine(vectors[left_index], vectors[right_index])
            flags = (edit_raw >= 0.80, jaccard_raw >= 0.70, cosine_raw >= 0.70)
            pair = {
                "id_a": left["exact_stimulus_id"],
                "id_b": right["exact_stimulus_id"],
                "edit_similarity": edit_raw,
                "token_jaccard": jaccard_raw,
                "embedding_cosine": cosine_raw,
            }
            pairs.append(pair)
            for name in metric_values:
                metric_values[name].append(pair[name])
            names = ("edit_080", "jaccard_070", "embedding_070")
            active = tuple(name for name, flag in zip(names, flags) if flag)
            for name in active:
                trigger_counts[name] += 1
            if len(active) >= 2:
                for first in range(len(active)):
                    for second in range(first + 1, len(active)):
                        intersections[f"{active[first]}__{active[second]}"] += 1
            if len(active) == 3:
                intersections["all_three"] += 1
            if any(flags):
                candidate = {
                    "id_a": pair["id_a"], "id_b": pair["id_b"],
                    "edit_similarity": round_half_even(edit_raw),
                    "token_jaccard": round_half_even(jaccard_raw),
                    "embedding_cosine": round_half_even(cosine_raw),
                    "trigger_edit_080": flags[0],
                    "trigger_jaccard_070": flags[1],
                    "trigger_embedding_070": flags[2],
                    "length_chars_a": left["length_chars"],
                    "length_chars_b": right["length_chars"],
                    "slots_a": left["slots"], "slots_b": right["slots"],
                }
                if set(candidate) != set(CANDIDATE_FIELDS):
                    _fail("CANDIDATE_FIELD_MISMATCH", pair["id_a"])
                candidates.append(candidate)
    expected_pairs = unordered_pair_count(expectations.unique_identities)
    if len(pairs) != expected_pairs:
        _fail("PAIR_COUNT_MISMATCH", f"{len(pairs)} expected={expected_pairs}")
    candidates.sort(key=lambda row: (row["id_a"], row["id_b"]))

    top_pairs = {}
    for metric in metric_values:
        ranked = sorted(pairs, key=lambda row: (-row[metric], row["id_a"], row["id_b"]))[:1000]
        top_pairs[metric] = [
            {"id_a": row["id_a"], "id_b": row["id_b"], "score": round_half_even(row[metric])}
            for row in ranked
        ]
    component_diagnostics = {}
    identities = [row["exact_stimulus_id"] for row in internal]
    for metric, cuts in COMPONENT_CUTS.items():
        component_diagnostics[metric] = [
            {
                "diagnostic_cut": cut,
                **_component_summary(
                    identities,
                    ((row["id_a"], row["id_b"]) for row in pairs if row[metric] >= cut),
                ),
            }
            for cut in cuts
        ]
    sorted_tokens = sorted(token_counts)
    wordpiece_quantiles = [
        {"q": format(Decimal(str(probability)), "f"), "value": round_half_even(_quantile(sorted_tokens, probability))}
        for probability in QUANTILES
    ]
    diagnostic = {
        "schema_version": 1,
        "artifact": "ZUCO2_NR_STIMULUS_SIMILARITY_DIAGNOSTIC_V1",
        "source_binding": {
            "path": outputs["source_binding"].relative_to(root.resolve()).as_posix(),
            "sha256": source_binding_hash,
        },
        "source_file_hashes": source_hashes,
        "committed_input_hashes": input_hashes,
        "embedding_model": {
            "repo_id": MODEL_REPO_ID,
            "revision": expected_model_revision,
            "license": MODEL_LICENSE,
            "dimension": expectations.model_dimension,
            "acquisition": model_acquisition,
            "files": model_inventory,
            "software_versions": versions,
            "device": "cpu",
            "eval_mode": True,
            "no_grad": True,
            "use_safetensors": True,
            "trust_remote_code": False,
            "pooling": "attention-mask mean pooling",
            "normalization": "float32 L2",
            "wordpieces": {
                "min": min(token_counts), "max": max(token_counts),
                "quantiles": wordpiece_quantiles,
                "limit": expectations.max_wordpieces,
                "truncation": False,
            },
        },
        "counts": {
            "material_rows": len(all_material), "practice_rows": len(practice_rows),
            "task_slots": len(task_rows), "unique_exact_identities": len(internal),
            "exact_duplicate_groups": len(exact_groups), "unordered_pairs": len(pairs),
        },
        "score_distributions": {
            "edit_similarity": _distribution(metric_values["edit_similarity"], 0.0, 1.0),
            "token_jaccard": _distribution(metric_values["token_jaccard"], 0.0, 1.0),
            "embedding_cosine": _distribution(metric_values["embedding_cosine"], -1.0, 1.0),
        },
        "top_pairs": top_pairs,
        "broad_diagnostic_prefilter": {
            "rule": "edit_similarity >= 0.80 OR token_jaccard >= 0.70 OR embedding_cosine >= 0.70",
            "final_grouping_threshold": False,
            "trigger_counts": {
                "edit_080": trigger_counts["edit_080"],
                "jaccard_070": trigger_counts["jaccard_070"],
                "embedding_070": trigger_counts["embedding_070"],
            },
            "pairwise_intersections": {
                key: intersections[key]
                for key in (
                    "edit_080__jaccard_070", "edit_080__embedding_070",
                    "jaccard_070__embedding_070",
                )
            },
            "triple_intersection": intersections["all_three"],
            "union_count": len(candidates),
        },
        "component_risk_diagnostics": component_diagnostics,
        "metadata_status": source_binding["metadata_availability"],
        "grouping_policy": {
            "status": "PENDING_GROUP_POLICY_REVIEW",
            "owner": "CHATGPT_OR_AUTHOR",
            "final_threshold_selected": False,
            "near_duplicate_groups_emitted": False,
            "paraphrase_verified": False,
            "split_constructed": False,
        },
        "safety": {
            "stimulus_text_emitted": False, "lexical_hash_emitted_in_candidates": False,
            "tokens_or_ngrams_emitted": False, "embedding_vectors_emitted": False,
            "remote_inference_used": False, "stimulus_text_sent_remote": False,
            "eeg_event_tsr_read": False, "outcome_or_historical_result_read": False,
            "checkpoint_read": False, "backbone_a_selected": False,
            "training_run": False, "gate_run": False,
        },
    }
    rendered = {
        outputs["source_binding"]: source_binding_bytes,
        outputs["diagnostic"]: _yaml_bytes(diagnostic),
        outputs["candidates"]: _jsonl_bytes(candidates),
        outputs["report"]: _report_bytes(diagnostic),
    }
    _atomic_write(rendered)
    return {
        "source_binding": source_binding,
        "diagnostic": diagnostic,
        "candidates": candidates,
        "output_sha256": {
            path.name: hashlib.sha256(content).hexdigest() for path, content in rendered.items()
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-root", type=Path, required=True)
    parser.add_argument("--targeted-manifest", type=Path, required=True)
    parser.add_argument("--stimulus-manifest", type=Path, required=True)
    parser.add_argument("--analysis-view", type=Path, required=True)
    parser.add_argument("--analysis-summary", type=Path, required=True)
    parser.add_argument("--data-card", type=Path, required=True)
    parser.add_argument("--model-dir", type=Path, required=True)
    parser.add_argument("--model-acquisition", choices=("DOWNLOADED", "REUSED_CACHE"), default="REUSED_CACHE")
    parser.add_argument("--output-source-binding", type=Path, required=True)
    parser.add_argument("--output-diagnostic", type=Path, required=True)
    parser.add_argument("--output-candidates", type=Path, required=True)
    parser.add_argument("--output-report", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        result = build(
            **vars(args), root=PROJECT_ROOT, committed_hashes=COMMITTED_INPUT_SHA256,
            enforce_basenames=True,
        )
    except DiagnosticError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    for name, digest in sorted(result["output_sha256"].items()):
        print(f"{name} {digest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
