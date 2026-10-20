"""SAFE ransomware *simulator* - a test trigger for RDRS, not malware.

It only ever works inside a sandbox folder, creates brand-new throwaway files,
overwrites them with random bytes (so they look encrypted) and renames them
to .locked. It refuses to run outside a folder named 'sandbox'.

    python -m simulator.attack_simulator --count 50 --delay 0.02
"""
from __future__ import annotations

import argparse
import os
import time
from pathlib import Path


def run(sandbox: Path, count: int = 50, delay: float = 0.0) -> int:
    if sandbox.name != "sandbox":
        raise SystemExit("Refusing to run: target folder must be named 'sandbox'.")
    sandbox.mkdir(parents=True, exist_ok=True)

    files = []
    for i in range(count):  # 1) create normal throwaway files
        f = sandbox / f"file_{i}.txt"
        f.write_text("normal document content " * 20)
        files.append(f)
    time.sleep(1)

    for f in files:  # 2) "encrypt": random bytes + extension change
        f.write_bytes(os.urandom(20000))
        f.rename(f.with_suffix(".locked"))
        time.sleep(delay)
    (sandbox / "README_DECRYPT.txt").write_text("SIMULATED ransom note - test only.")
    return count


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--sandbox", default="data/sandbox")
    ap.add_argument("--count", type=int, default=50)
    ap.add_argument("--delay", type=float, default=0.0)
    a = ap.parse_args()
    n = run(Path(a.sandbox), a.count, a.delay)
    print(f"Simulated attack on {n} files in {a.sandbox}")

