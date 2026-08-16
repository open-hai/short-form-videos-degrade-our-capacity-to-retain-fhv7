"""Figures 3-6 of the paper, re-drawn from the trial-level data.

These are re-implementations, not restyled copies: the paper's own figures are
produced by `2.response_accuracy_vis.ipynb`, `4.ddm_feature_vis.ipynb` and
`5.ddm_tiktok_vis.ipynb` with a LaTeX font stack that is not assumed here.  What
is checked is that the same data produce the same qualitative picture.
"""

from __future__ import annotations

import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ORDER = ["rest", "twitter", "youtube", "tiktok"]
LABEL = {"rest": "Rest", "twitter": "Twitter", "youtube": "YouTube", "tiktok": "TikTok"}


def figure3(trials: pd.DataFrame, outdir: str) -> list[str]:
    """RT densities for correct vs error responses, per condition and block."""
    paths = []
    for task in ("LD", "PM"):
        fig, axes = plt.subplots(2, 4, figsize=(13, 5), sharex=True, sharey=True)
        for col, cond in enumerate(ORDER):
            for row, measure in enumerate(("pre", "post")):
                ax = axes[row][col]
                sub = trials[
                    (trials.task == task)
                    & (trials.interrupt == cond)
                    & (trials.measure == measure)
                    & (trials.success)
                ]
                for correct, color in ((True, "tab:blue"), (False, "tab:red")):
                    rts = sub[sub.correct == correct].rt * 1000
                    if len(rts) > 2:
                        ax.hist(
                            rts,
                            bins=np.linspace(0, 3000, 40),
                            density=True,
                            histtype="stepfilled",
                            alpha=0.5,
                            color=color,
                            label="Correct" if correct else "Error",
                        )
                if row == 0:
                    ax.set_title(LABEL[cond])
                if col == 0:
                    ax.set_ylabel(f"Density ({measure}-interruption)")
                ax.set_xlabel("RTs (ms)")
        axes[0][0].legend(fontsize=8)
        fig.suptitle(f"Figure 3 reproduction - {task} task")
        fig.tight_layout()
        path = os.path.join(outdir, f"fig3_rt_{task.lower()}.png")
        fig.savefig(path, dpi=140)
        plt.close(fig)
        paths.append(path)
    return paths


def figure4(acc: pd.DataFrame, outdir: str) -> str:
    """Pre/post response accuracy per condition, for LD and PM."""
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    for ax, task, title in zip(axes, ("LD", "PM"), ("Lexical Decision Task", "Prospective Memory Task")):
        d = acc[acc.task == task]
        width = 0.38
        x = np.arange(len(ORDER))
        for i, measure in enumerate(("pre", "post")):
            means = [d[(d.interrupt == c) & (d.measure == measure)].accuracy.mean() * 100 for c in ORDER]
            errs = [
                d[(d.interrupt == c) & (d.measure == measure)].accuracy.sem() * 100 for c in ORDER
            ]
            ax.bar(x + (i - 0.5) * width, means, width, yerr=errs, capsize=3, label=f"Task {measure}")
        ax.set_xticks(x, [LABEL[c] for c in ORDER])
        ax.set_ylim(0, 100)
        ax.set_ylabel("Response Accuracy (%)")
        ax.set_title(title)
        ax.legend()
    fig.suptitle("Figure 4 reproduction")
    fig.tight_layout()
    path = os.path.join(outdir, "fig4_accuracy.png")
    fig.savefig(path, dpi=140)
    plt.close(fig)
    return path


def figure5(ddm: pd.DataFrame, outdir: str) -> str:
    """Fitted DDM parameters in the PM task, pre vs post, per condition."""
    params = [("drift", "Drift (mu)"), ("noise", "Variance (sigma)"), ("bound", "Bound (B)"), ("nondectime", "Non-decision Time (t)")]
    d = ddm[ddm.task == "PM"]
    fig, axes = plt.subplots(1, 4, figsize=(15, 4))
    for ax, (param, title) in zip(axes, params):
        for i, measure in enumerate(("pre", "post")):
            data = [d[(d.interrupt == c) & (d.measure == measure)][param].values for c in ORDER]
            positions = np.arange(len(ORDER)) + (i - 0.5) * 0.3
            bp = ax.boxplot(data, positions=positions, widths=0.25, patch_artist=True)
            for box in bp["boxes"]:
                box.set_facecolor("tab:blue" if measure == "pre" else "tab:orange")
                box.set_alpha(0.6)
        ax.set_xticks(np.arange(len(ORDER)), [LABEL[c] for c in ORDER], rotation=20)
        ax.set_title(title)
    handles = [
        plt.Rectangle((0, 0), 1, 1, color="tab:blue", alpha=0.6),
        plt.Rectangle((0, 0), 1, 1, color="tab:orange", alpha=0.6),
    ]
    axes[0].legend(handles, ["pre", "post"], fontsize=8)
    fig.suptitle("Figure 5 reproduction - fitted DDM parameters, PM task")
    fig.tight_layout()
    path = os.path.join(outdir, "fig5_ddm_pm.png")
    fig.savefig(path, dpi=140)
    plt.close(fig)
    return path


def figure6(trials: pd.DataFrame, pooled_fit: dict, outdir: str) -> str:
    """TikTok PM RT distributions pre and post, annotated with the pooled fit."""
    fig, axes = plt.subplots(2, 1, figsize=(8, 6), sharex=True)
    sub = trials[(trials.task == "PM") & (trials.interrupt == "tiktok") & (trials.success)]
    for ax, measure in zip(axes, ("pre", "post")):
        s = sub[sub.measure == measure]
        ax.hist(s[s.correct].rt * 1000, bins=40, color="tab:blue", alpha=0.6, label="correct")
        ax.hist(s[~s.correct].rt * 1000, bins=40, color="tab:red", alpha=0.6, label="error")
        fit = pooled_fit[measure]
        ax.set_title(
            f"TikTok {measure}-interruption: accuracy {fit['accuracy'] * 100:.2f}%  |  "
            f"mu={fit['drift']:.2f}, sigma={fit['noise']:.2f}, "
            f"B={fit['bound']:.2f}, t={fit['nondectime'] * 1000:.0f} ms, loss={fit['loss']:.2f}",
            fontsize=9,
        )
        ax.set_ylabel("Counts")
        ax.legend(fontsize=8)
    axes[-1].set_xlabel("RTs (ms)")
    fig.suptitle("Figure 6 reproduction - pooled TikTok PM fits")
    fig.tight_layout()
    path = os.path.join(outdir, "fig6_ddm_tiktok.png")
    fig.savefig(path, dpi=140)
    plt.close(fig)
    return path
