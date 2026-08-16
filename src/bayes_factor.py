"""JZS Bayes factors for the one-way questionnaire ANOVAs (Section 4.2).

The paper reports BF01 for Engagement, SUQ-A and BSMAS but never states which
Bayes factor: no prior scale, no software.  `6.questionnaire_bayes_factor.ipynb`
shows `BayesFactor::anovaBF` with its defaults, i.e. a JZS g-prior with
rscaleFixed = 0.5.  That default is assumed here (decision D8).

For a balanced one-way design with J levels and n observations per level the
marginal likelihood ratio conditional on g has the closed form

    BF10(g) = (1 + n g)^(-(J-1)/2) * (1 - (n g / (1 + n g)) R^2)^(-(N-1)/2)

with R^2 the proportion of total sum of squares due to the factor; the JZS prior
g ~ InverseGamma(1/2, r^2/2) is then integrated out numerically.  BayesFactor
does that integral by Monte Carlo, so its published values carry ~1% noise; this
implementation uses quadrature.
"""

from __future__ import annotations

import numpy as np
from scipy.integrate import quad
from scipy.special import gammaln


def jzs_oneway_bf10(y, group, r: float = 0.5) -> float:
    y = np.asarray(y, dtype=float)
    group = np.asarray(group)
    levels = np.unique(group)
    counts = np.array([(group == lev).sum() for lev in levels])
    if len(set(counts)) != 1:
        raise ValueError("this closed form assumes a balanced design")
    n = int(counts[0])
    J = len(levels)
    N = len(y)
    grand = y.mean()
    ss_total = float(((y - grand) ** 2).sum())
    ss_effect = float(
        sum((group == lev).sum() * (y[group == lev].mean() - grand) ** 2 for lev in levels)
    )
    r2 = ss_effect / ss_total

    def integrand(g: float) -> float:
        if g <= 0:
            return 0.0
        log_bf = -(J - 1) / 2 * np.log1p(n * g) - (N - 1) / 2 * np.log(
            1 - (n * g / (1 + n * g)) * r2
        )
        log_prior = (
            0.5 * np.log(r**2 / 2) - gammaln(0.5) - 1.5 * np.log(g) - r**2 / (2 * g)
        )
        return float(np.exp(log_bf + log_prior))

    value, _ = quad(integrand, 0, np.inf, limit=500)
    return value


def questionnaire_tests(q, scales=("ENGAGE", "SUQ", "BSMARS")) -> list[dict]:
    import pingouin as pg

    rows = []
    for scale in scales:
        if scale not in q.columns:
            continue
        aov = pg.anova(data=q, dv=scale, between="interrupt", detailed=True)
        row = aov.iloc[0]
        bf10 = jzs_oneway_bf10(q[scale], q["interrupt"])
        rows.append(
            {
                "scale": scale,
                "F": float(row["F"]),
                "df1": int(row["DF"]),
                "df2": int(aov.iloc[1]["DF"]),
                "p": float(row["p_unc"]),
                "np2": float(row["np2"]),
                "BF10": bf10,
                "BF01": 1.0 / bf10,
            }
        )
    return rows
