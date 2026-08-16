"""Loading and schema validation for the trial-level data.

The analysis entrypoint consumes one trial-level CSV.  The schema below is the
one used by the authors' released `rt.csv` (mimuc/media-prospective-memory), and
is the schema declared in `instrument.json` so the same pipeline can be run on a
new dataset.
"""

from __future__ import annotations

import sys

import pandas as pd

REQUIRED_COLUMNS = {
    "folder_id": "participant identifier (int or str)",
    "task": "LD | PM  (which task the trial was scored as)",
    "interrupt": "rest | twitter | youtube | tiktok  (between-subjects condition)",
    "measure": "pre | post | train  (experimental block)",
    "stimulus": "the letter string shown on that trial",
    "success": "bool, True if the participant produced a key press",
    "correct": "bool, True if the key press was the correct one",
    "rt": "reaction time in seconds (NaN when success is False)",
}

# The three PM cue words of the paper (Section 3.2, Figure 1).
PM_CUES = ("BLAU", "LILA", "GRÜN")

CONDITIONS = ["rest", "twitter", "youtube", "tiktok"]


def load_trials(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise SystemExit(
            f"input {path} is missing required column(s): {missing}\n"
            "expected schema:\n  "
            + "\n  ".join(f"{k}: {v}" for k, v in REQUIRED_COLUMNS.items())
        )
    for col in ("success", "correct"):
        if df[col].dtype != bool:
            df[col] = df[col].astype(str).str.lower().isin(["true", "1", "yes"])
    df["rt"] = pd.to_numeric(df["rt"], errors="coerce")
    return df


def describe_trials(df: pd.DataFrame) -> dict:
    """Descriptives used to check the released data against the reported design."""
    exp = df[df.measure != "train"]
    cue = df["stimulus"].astype(str).str.upper().isin(PM_CUES)
    per_block = (
        exp[cue.loc[exp.index]]
        .groupby(["folder_id", "measure"])
        .size()
    )
    return {
        "n_participants": int(df.folder_id.nunique()),
        "participants_per_condition": {
            k: int(v) for k, v in df.groupby("interrupt").folder_id.nunique().items()
        },
        "n_trials_total": int(len(df)),
        "n_trials_by_block_and_task": {
            f"{m}/{t}": int(n)
            for (m, t), n in df.groupby(["measure", "task"]).size().items()
        },
        "no_response_trials": int((~df.success).sum()),
        "pm_cue_trials_per_participant_per_block": {
            "mean": float(per_block.mean()),
            "min": int(per_block.min()),
            "max": int(per_block.max()),
        },
        "trials_labelled_PM_without_a_PM_cue_stimulus": int(
            ((df.task == "PM") & (~cue)).sum()
        ),
        "trials_labelled_LD_with_a_PM_cue_stimulus": int(
            ((df.task == "LD") & cue).sum()
        ),
    }


def eprint(*a):
    print(*a, file=sys.stderr)
