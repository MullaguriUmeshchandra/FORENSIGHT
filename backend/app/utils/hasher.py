import hashlib
from typing import BinaryIO, Union
from pathlib import Path

def compute_sha256_bytes(data: bytes) -> str:
    """Compute SHA-256 hash of bytes."""
    sha256 = hashlib.sha256()
    sha256.update(data)
    return sha256.hexdigest()

def compute_sha256_stream(file_obj: BinaryIO, chunk_size: int = 65536) -> str:
    """Compute SHA-256 hash of a file-like stream without loading whole file into memory."""
    sha256 = hashlib.sha256()
    file_obj.seek(0)
    while chunk := file_obj.read(chunk_size):
        sha256.update(chunk)
    file_obj.seek(0)
    return sha256.hexdigest()

def compute_sha256_file(filepath: Union[str, Path], chunk_size: int = 65536) -> str:
    """Compute SHA-256 hash of a file on disk."""
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    sha256 = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(chunk_size):
            sha256.update(chunk)
    return sha256.hexdigest()
