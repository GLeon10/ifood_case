import gzip
import io
import json
import os
import tarfile
from pathlib import Path
from typing import Generator, Iterable, Optional

import pandas as pd
import requests


BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DATA_DIR = BASE_DIR / "data" / "raw"


def ensure_raw_dir() -> None:
    """Ensure raw data directory exists."""
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)


def download_file(url: str, path: str | os.PathLike, chunk_size: int = 1024 * 1024) -> Path:
    """
    Download a file from a URL to the given path using streaming.

    Parameters
    ----------
    url : str
        Source URL.
    path : str | os.PathLike
        Destination file path.
    chunk_size : int
        Chunk size in bytes for streaming download.
    """
    ensure_raw_dir()
    dest_path = Path(path)
    if not dest_path.is_absolute():
        dest_path = RAW_DATA_DIR / dest_path
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    with requests.get(url, stream=True, timeout=60) as r:
        r.raise_for_status()
        with open(dest_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)

    return dest_path


def extract_gzip(path: str | os.PathLike, dest_path: Optional[str | os.PathLike] = None) -> Path:
    """
    Extract a .gz file to the destination path.

    If dest_path is not provided, removes the .gz suffix in the same directory.
    """
    src = Path(path)
    if dest_path is None:
        if src.suffix == ".gz":
            dest = src.with_suffix("")
        else:
            dest = src.with_suffix(src.suffix + ".out")
    else:
        dest = Path(dest_path)
        if not dest.is_absolute():
            dest = src.parent / dest

    with gzip.open(src, "rb") as f_in, open(dest, "wb") as f_out:
        for chunk in iter(lambda: f_in.read(1024 * 1024), b""):
            f_out.write(chunk)

    return dest


def extract_tar(path: str | os.PathLike, dest_dir: Optional[str | os.PathLike] = None) -> Path:
    """
    Extract a .tar or .tar.gz archive to the destination directory.

    Returns the destination directory path.
    """
    src = Path(path)
    if dest_dir is None:
        dest = src.parent / src.stem
    else:
        dest = Path(dest_dir)
        if not dest.is_absolute():
            dest = src.parent / dest

    dest.mkdir(parents=True, exist_ok=True)

    mode = "r:gz" if src.suffixes[-2:] == [".tar", ".gz"] or src.suffix == ".gz" else "r:"
    with tarfile.open(src, mode) as tar:
        tar.extractall(path=dest)

    return dest


def load_orders_json_streaming(path: str | os.PathLike, chunksize: int = 100_000) -> Iterable[pd.DataFrame]:
    """
    Load a large JSON orders file in streaming fashion, yielding DataFrame chunks.

    Assumes the file is line-delimited JSON (one order per line).

    Parameters
    ----------
    path : str | os.PathLike
        Path to the JSON file (already uncompressed).
    chunksize : int
        Number of records per yielded DataFrame.
    """
    src = Path(path)
    if not src.is_absolute():
        src = RAW_DATA_DIR / src

    buffer: list[dict] = []
    with open(src, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
                buffer.append(record)
            except json.JSONDecodeError:
                # Skip malformed lines to keep pipeline robust
                continue

            if len(buffer) >= chunksize:
                yield pd.DataFrame(buffer)
                buffer.clear()

    if buffer:
        yield pd.DataFrame(buffer)


__all__ = [
    "download_file",
    "extract_gzip",
    "extract_tar",
    "load_orders_json_streaming",
    "RAW_DATA_DIR",
]

