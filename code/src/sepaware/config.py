from __future__ import annotations

import hashlib
import os
from pathlib import Path

import yaml


def repository_root() -> Path:
    return Path(__file__).resolve().parents[3]


def load_manifest(path: str | Path) -> dict:
    path = Path(path)
    with path.open(encoding="utf-8") as stream:
        config = yaml.safe_load(stream)
    config["_manifest_path"] = str(path.resolve())
    return config


def data_root() -> Path:
    value = os.environ.get("SEPAWARE_DATA_ROOT")
    if not value:
        raise RuntimeError("Set SEPAWARE_DATA_ROOT to the authorized directory containing the four source files.")
    return Path(value).expanduser().resolve()


def sha1(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha1()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_source(path: Path, expected_sha1: str) -> None:
    if not path.is_file():
        raise FileNotFoundError(path)
    observed = sha1(path)
    if observed != expected_sha1:
        raise ValueError(f"Source hash mismatch for {path.name}: expected {expected_sha1}, observed {observed}")
