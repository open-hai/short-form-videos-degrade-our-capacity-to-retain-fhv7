"""Drift-Diffusion Model fitting (Section 3.6, 4.1.3, Figure 6).

The paper says only that PyDDM was used to fit "responses in the LD and PM tasks
per participant" (Section 4.1.3).  Everything else -- the four free parameters,
their search ranges, the loss function, the optimiser, the spatial and temporal
discretisation, the trial cut-off -- comes from the authors' released notebook
`appendix2_ddm_fitting.ipynb`, not from the paper.  Those values are repeated
here so that the fit can be reproduced without the notebook, and so that the
sensitivity to `dt` can be measured (decision D6).
"""

from __future__ import annotations

import time

import pandas as pd
from pyddm import Fittable, Model, Sample
from pyddm.functions import fit_adjust_model
from pyddm.models import (
    BoundConstant,
    DriftConstant,
    LossRobustBIC,
    NoiseConstant,
    OverlayNonDecision,
)

# Search ranges taken from appendix2_ddm_fitting.ipynb; the paper states none.
DRIFT_RANGE = (0, 50)
NOISE_RANGE = (0.5, 4)
BOUND_RANGE = (0.1, 2)
NONDEC_RANGE = (0, 1)
T_DUR = 3


def fit_cell(df: pd.DataFrame, dx: float = 0.001, dt: float = 0.001) -> dict:
    """Fit one constant-drift DDM to one set of trials."""
    df = df[df.success].dropna(subset=["rt"])
    sample = Sample.from_pandas_dataframe(
        df, rt_column_name="rt", choice_column_name="correct"
    )
    model = Model(
        name="ddm",
        drift=DriftConstant(drift=Fittable(minval=DRIFT_RANGE[0], maxval=DRIFT_RANGE[1])),
        noise=NoiseConstant(noise=Fittable(minval=NOISE_RANGE[0], maxval=NOISE_RANGE[1])),
        bound=BoundConstant(B=Fittable(minval=BOUND_RANGE[0], maxval=BOUND_RANGE[1])),
        overlay=OverlayNonDecision(
            nondectime=Fittable(minval=NONDEC_RANGE[0], maxval=NONDEC_RANGE[1])
        ),
        dx=dx,
        dt=dt,
        T_dur=T_DUR,
    )
    fit_adjust_model(
        sample,
        model,
        fitting_method="differential_evolution",
        lossfunction=LossRobustBIC,
        verbose=False,
    )
    drift, noise, bound, nondectime = (p.default() for p in model.get_model_parameters())
    return {
        "drift": float(drift),
        "noise": float(noise),
        "bound": float(bound),
        "nondectime": float(nondectime),
        "loss": float(model.get_fit_result().value()),
        "n_trials": int(len(df)),
        "accuracy": float(df.correct.mean()),
    }


def fit_all_cells(
    trials: pd.DataFrame, dx: float = 0.001, dt: float = 0.001, progress=None
) -> pd.DataFrame:
    """One DDM per participant x task x block (the 240 fits behind Table 1)."""
    rows = []
    exp = trials[trials.measure.isin(["pre", "post"])]
    ids = sorted(exp.folder_id.unique())
    total = len(ids) * 4
    done = 0
    t0 = time.time()
    for folder_id in ids:
        for measure in ("pre", "post"):
            for task in ("LD", "PM"):
                sub = exp[
                    (exp.folder_id == folder_id)
                    & (exp.measure == measure)
                    & (exp.task == task)
                ]
                if len(sub[sub.success]) < 5:
                    continue
                fit = fit_cell(sub, dx=dx, dt=dt)
                fit.update(
                    folder_id=folder_id,
                    interrupt=sub.interrupt.iloc[0],
                    task=task,
                    measure=measure,
                )
                rows.append(fit)
                done += 1
                if progress and done % 20 == 0:
                    progress(f"  ddm fits {done}/{total} ({time.time() - t0:.0f}s)")
    cols = [
        "folder_id",
        "interrupt",
        "task",
        "measure",
        "drift",
        "noise",
        "bound",
        "nondectime",
        "loss",
        "n_trials",
        "accuracy",
    ]
    return pd.DataFrame(rows)[cols]


def fit_pooled_tiktok(trials: pd.DataFrame, dx: float = 0.001, dt: float = 0.0001) -> dict:
    """The aggregate fits behind Figure 6: all TikTok PM trials, pre and post."""
    out = {}
    sub = trials[(trials.task == "PM") & (trials.interrupt == "tiktok")]
    for measure in ("pre", "post"):
        out[measure] = fit_cell(sub[sub.measure == measure], dx=dx, dt=dt)
    return out
