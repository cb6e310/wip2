#!/usr/bin/env python3
"""Deterministic, metadata-first inventory of two explicitly authorized roots."""

from __future__ import annotations

import argparse
import hashlib
import os
import stat
from pathlib import Path
from typing import Any, Iterator

import yaml


EXCLUDED_DIRS = {".git", ".venv", "__pycache__", ".cache", "cache", "node_modules", "tmp", "temp"}
RESULT_DIR_NAMES = {"results", "result", "outputs", "output", "logs", "log", "wandb", "predictions", "eval", "test_results", "03_runs", "04_results"}
REFERENCE_METADATA_ONLY_DIRS = {"artifacts", "reports", "runs", "candidates", "splits"}
UNSAFE_SUFFIXES = {".pkl", ".pickle", ".joblib", ".pt", ".pth", ".ckpt"}
DATA_SUFFIXES = {".mat", ".set", ".fdt", ".edf", ".bdf", ".cnt", ".h5", ".hdf5", ".npy", ".npz", ".parquet", ".csv", ".tsv", ".json"}
SECRET_NAMES = {".env", ".netrc", "credentials", "credentials.json", "id_rsa", "id_ed25519", "known_hosts"}
SAFE_HASH_SUFFIXES = {
    "", ".py", ".md", ".txt", ".yaml", ".yml", ".toml", ".ini", ".cfg",
    ".json", ".lock", ".csv", ".tsv", ".sh", ".ps1", ".license",
}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _relative(root: Path, path: Path) -> str:
    value = path.relative_to(root).as_posix()
    return value or "."


def _is_secret_name(path: Path) -> bool:
    lower = path.name.lower()
    return lower in SECRET_NAMES or any(token in lower for token in ("credential", "secret", "token"))


def _record(root_label: str, root: Path, path: Path, max_hash: int) -> dict[str, Any]:
    info = path.lstat()
    item: dict[str, Any] = {
        "root": root_label,
        "path": _relative(root, path),
        "size_bytes": info.st_size,
        "mtime_ns": info.st_mtime_ns,
    }
    mode = info.st_mode
    if stat.S_ISLNK(mode):
        target = path.resolve(strict=False)
        item.update(type="symlink", link_target=os.readlink(path), resolved_target=str(target), followed=False)
        return item
    if stat.S_ISDIR(mode):
        item["type"] = "directory"
        return item
    if not stat.S_ISREG(mode):
        item.update(type="special", content_read=False)
        return item
    item["type"] = "file"
    suffix = path.suffix.lower()
    if _is_secret_name(path):
        item.update(hash_status="HASH_SKIPPED_SENSITIVE_NAME", content_read=False)
    elif suffix in UNSAFE_SUFFIXES:
        item.update(hash_status="HASH_SKIPPED_UNSAFE_FORMAT", content_read=False)
    elif suffix in DATA_SUFFIXES:
        item.update(hash_status="HASH_SKIPPED_DATA_FORMAT", content_read=False)
    elif info.st_size > max_hash:
        item.update(hash_status="HASH_SKIPPED_TOO_LARGE", content_read=False)
    elif suffix not in SAFE_HASH_SUFFIXES:
        item.update(hash_status="HASH_SKIPPED_BINARY_OR_DATA", content_read=False)
    else:
        item.update(hash_status="SHA256", sha256=_sha256(path), content_read=True)
    return item


def _walk(root_label: str, root: Path, max_hash: int) -> Iterator[dict[str, Any]]:
    pending = [root]
    while pending:
        directory = pending.pop()
        try:
            children = sorted(directory.iterdir(), key=lambda p: p.name.casefold())
        except OSError as exc:
            yield {"root": root_label, "path": _relative(root, directory), "type": "unreadable_directory", "error": type(exc).__name__}
            continue
        for path in children:
            relative = _relative(root, path)
            try:
                item = _record(root_label, root, path, max_hash)
            except OSError as exc:
                yield {"root": root_label, "path": relative, "type": "unreadable", "error": type(exc).__name__}
                continue
            name = path.name.lower()
            reference_history = root_label == "reference" and (
                name in REFERENCE_METADATA_ONLY_DIRS or name.startswith(".codex_stage0")
            )
            if item["type"] == "directory" and (name in RESULT_DIR_NAMES or reference_history):
                item.update(classification="UNREAD_HISTORICAL_RESULT", content_read=False, recursive_scan=False)
            elif item["type"] == "directory" and name in EXCLUDED_DIRS:
                item.update(classification="EXCLUDED_DIRECTORY", content_read=False, recursive_scan=False)
            yield item
            if item["type"] == "directory" and name not in RESULT_DIR_NAMES and name not in EXCLUDED_DIRS and not reference_history:
                pending.append(path)


def audit(project_root: Path, reference_root: Path, max_hash: int) -> dict[str, Any]:
    roots = {"project": project_root.resolve(), "reference": reference_root.resolve()}
    if max_hash < 0:
        raise ValueError("max-small-hash-bytes must be non-negative")
    if roots["project"] == roots["reference"]:
        raise ValueError("project and reference roots must differ")
    for label, root in roots.items():
        if not root.is_dir():
            raise ValueError(f"{label} root is not a directory: {root}")
    entries = [item for label, root in roots.items() for item in _walk(label, root, max_hash)]
    entries.sort(key=lambda item: (item["root"], item["path"]))
    return {
        "schema_version": 1,
        "audit_mode": "METADATA_FIRST_OUTCOME_BLIND",
        "authorized_roots": {label: str(root) for label, root in roots.items()},
        "max_small_hash_bytes": max_hash,
        "exclusions": sorted(EXCLUDED_DIRS),
        "historical_result_content_read": False,
        "unsafe_format_deserialized": False,
        "secret_values_recorded": False,
        "entries": entries,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", required=True, type=Path)
    parser.add_argument("--reference-root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--max-small-hash-bytes", type=int, default=1_048_576)
    args = parser.parse_args()
    payload = audit(args.project_root, args.reference_root, args.max_small_hash_bytes)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    rendered = yaml.safe_dump(payload, sort_keys=False, allow_unicode=True)
    args.output.write_text(rendered, encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
