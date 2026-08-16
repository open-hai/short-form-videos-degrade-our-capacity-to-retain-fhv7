"""Emit a schema-conformant *fake* trial file, to check the {{INPUT}} contract.

This is a pipeline test, not a study. The numbers it writes are random noise with
no experimental manipulation in them: they exist only to prove that
`src/analyze.py` runs on a dataset it has never seen, with the columns declared
in `instrument.json`. Nothing produced from this file says anything about
prospective memory, about social media, or about what a study would have found,
and no output of it appears anywhere in the audit.

    python src/make_synthetic_input.py --out /tmp/fake_trials.csv
"""

from __future__ import annotations

import argparse

import numpy as np
import pandas as pd

CONDITIONS = ["rest", "twitter", "youtube", "tiktok"]
CUES = ["BLAU", "LILA", "GRÜN"]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="/tmp/fake_trials.csv")
    ap.add_argument("--participants-per-condition", type=int, default=6)
    ap.add_argument("--ld-trials", type=int, default=40)
    ap.add_argument("--pm-trials", type=int, default=10)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    rng = np.random.default_rng(args.seed)
    words = [f"WORT{i:03d}" for i in range(60)]
    rows = []
    pid = 100
    for condition in CONDITIONS:
        for _ in range(args.participants_per_condition):
            pid += 1
            for measure in ("pre", "post"):
                for _ in range(args.ld_trials):
                    rows.append((pid, "LD", condition, measure, rng.choice(words)))
                for _ in range(args.pm_trials):
                    rows.append((pid, "PM", condition, measure, rng.choice(CUES)))
    df = pd.DataFrame(rows, columns=["folder_id", "task", "interrupt", "measure", "stimulus"])
    df["success"] = rng.random(len(df)) > 0.02
    df["correct"] = df["success"] & (rng.random(len(df)) > 0.2)
    df["rt"] = np.where(df["success"], rng.gamma(4, 0.15, len(df)) + 0.3, np.nan)
    df.to_csv(args.out, index=False)
    print(f"wrote {args.out}: {len(df)} random trials, {df.folder_id.nunique()} fake participants")
    print("these values are noise; they are not a simulation of the study")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
