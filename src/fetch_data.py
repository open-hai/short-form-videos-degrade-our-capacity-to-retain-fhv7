"""Fetch the authors' released dataset to a directory outside this repository.

The data are CC-0 (github.com/mimuc/media-prospective-memory, osf.io/kzxy7) but
they are not this repo's work, so they are never committed here.

    python src/fetch_data.py --dest /tmp/mpm-data
"""

from __future__ import annotations

import argparse
import os
import urllib.request

BASE = "https://raw.githubusercontent.com/mimuc/media-prospective-memory/main/data"
FILES = ["rt.csv", "acc.csv", "ddm.csv", "q.csv"]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dest", default="/tmp/mpm-data")
    args = ap.parse_args()
    os.makedirs(args.dest, exist_ok=True)
    for name in FILES:
        url = f"{BASE}/{name}"
        target = os.path.join(args.dest, name)
        urllib.request.urlretrieve(url, target)
        print(f"{url} -> {target} ({os.path.getsize(target)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
