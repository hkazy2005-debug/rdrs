"""Shannon entropy helpers.

Encrypted (or compressed) data looks like random noise, so its entropy is
close to 8 bits per byte. Ordinary text sits around 3-5.
"""
from __future__ import annotations

import math
from collections import Counter
from pathlib import Path

MAX_ENTROPY = 8.0


def shannon_entropy(data: bytes) -> float:
    """Return the Shannon entropy of data from 0.0 to 8.0 bits per byte."""
    if not data:
        return 0.0
    total = len(data)
    entropy = 0.0
    for count in Counter(data).values():
        p = count / total
        entropy -= p * math.log2(p)
    return min(max(entropy, 0.0), MAX_ENTROPY)


def file_entropy(path: str | Path, sample_bytes: int = 65536) -> float:
    """Return the entropy of the first sample_bytes of a file.

    Sampling keeps this fast on big files. A missing or unreadable file
    returns 0.0 so the monitor never crashes on a file that vanished.
    """
    try:
        with open(path, "rb") as handle:
            return shannon_entropy(handle.read(sample_bytes))
    except (OSError, PermissionError):
        return 0.0

    