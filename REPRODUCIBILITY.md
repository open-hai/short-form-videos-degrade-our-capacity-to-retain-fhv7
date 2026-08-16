# Reproducibility verdict

**Paper:** Chiossi, Haliburton, Ou, Butz & Schmidt, *Short-Form Videos Degrade Our Capacity to
Retain Intentions: Effect of Context Switching On Prospective Memory*, CHI '23,
[doi:10.1145/3544548.3580778](https://doi.org/10.1145/3544548.3580778).

**Verdict: partial.** The paper's central empirical claim reproduces exactly from the released
data — prospective-memory accuracy collapses after a TikTok interruption and nowhere else, with
the published coefficients, confidence intervals and t values recovered to the precision they are
printed at. Six components come back only partially and one is blocked. The most consequential
finding of this audit is not a failure to reproduce a number but a modelling one: the fitted DDM
parameters that Table 1, Figure 5 and Figure 6 report are **not identified** by the model as
specified, so their published values are one draw of an unseeded stochastic optimiser — refitted
decision bounds correlate r = 0.17 with the published ones while the ratios the model does identify
correlate r > 0.99. Table 1's PM conclusions do survive a refit at the authors' own settings; its
individual F values and its "no significance in the LD task" do not.

---

## 1. Per-component reproduction table

Inner-loop components only; outer-loop components are listed in §2 and are never scored.
Every row states the evidence or the specific blocker. All runs use the authors' released CC-0
data (`rt.csv`, `q.csv`, and for I8/I14 their `ddm.csv`), consumed by `src/analyze.py`.

| # | Component (citation) | Outcome | Evidence / blocker |
|---|---|---|---|
| I1 | Response-accuracy derivation from trial data (Section 4.1.1, "total number of correct key presses divided by the total number of key presses") | **reproduced** | My independent derivation matches the authors' released `acc.csv` on all 240 rows, max abs difference 1.1e-16 |
| I2 | LD accuracy LMM, `accuracy ~ interrupt + (1\|folder_id)` (Section 4.1.1, *Lexical Decision Task*) | **reproduced** | β = −0.001 / 0.005 / −0.067 vs reported −.001 / .005 / −.07; t(114) = −0.03 / 0.11 / −1.47, all three identical to the paper; intercept CI [0.916, 1.042] vs [0.92, 1.04]. **Mismatch:** the paper's "R² = 0.67" is not this model's R² — conditional R² = 0.99, marginal 0.05 |
| I3 | PM accuracy LMM, `accuracy ~ interrupt * measure + (1\|folder_id)` (Section 4.1.1, *Prospective Memory Task*) | **reproduced** | Intercept 0.487, CI [0.40, 0.57], t(110) = 10.94; Rest β = 0.456 t = 7.25, Twitter 0.489 / 7.77, YouTube 0.342 / 5.42, pre 0.314 / 6.70 — every t identical to the paper, every β within 0.005, R²c = 0.667 vs 0.67 |
| I4 | Combined LD-vs-PM accuracy LMM (Section 4.1.1, *Behavioral accuracy Comparison*) | **reproduced** | TikTok×PM β = −0.277, t(230) = −5.01 vs reported −0.28, −5.01; Twitter×PM −0.005 / −0.10; YouTube×PM −0.025 / −0.46; R²c = 0.380 vs 0.38 |
| I5 | Trial-level binomial model with per-item and per-participant effects (footnote 2) | **partial** | Same reference cell, same ordering and sign as the released lme4 output (PM: Rest +3.24, Twitter +3.61, YouTube +1.89, pre +1.65 against lme4's +3.54 / +4.23 / +2.33 / +1.87). Blocker: statsmodels has no Laplace/AGQ binomial GLMM with crossed random effects, so this is a variational-Bayes approximation; the authors' own lme4 fit reports non-convergence (`max\|grad\| = 1.07`) |
| I6 | Reaction-time GLMMs (Section 4.1.2, "we did not report any significant results") | **partial** | Blocker: no Gamma GLMM with crossed random effects exists in Python; a log-normal LMM on the same trials is used instead, and it lands within 0.01 of the authors' released Gamma-log coefficients. **Mismatch (contradiction):** that model does find significant effects — LD RT TikTok×post β = −0.053, t = −5.17, p < .001, and PM RT YouTube×post β = −0.082, t = −2.69, p = .007. The authors' own released notebook `appendix1` reports exactly the same two effects (−0.05, p < .001 and −0.08, p = .010), so the paper's "no significant results" is contradicted by its own supplement |
| I7 | Per-participant DDM fits, 240 cells (Sections 3.6, 4.1.3) | **partial** | Refitting all 240 cells at the authors' own dt = 1e-4 recovers non-decision time (r = 0.998, 0.3 % median deviation) but not the other three parameters: drift r = 0.89, noise r = 0.79, **bound r = 0.17**, each ~14 % median deviation. The ratios do come back: drift/noise r = 0.999, bound/noise r = 0.991. The model as specified (σ free, no seed) is identified only up to a common scale factor, so no refit can be expected to land on the published values |
| I8 | Two-way ANOVAs on the DDM parameters, Table 1 (Section 4.1.3) | **reproduced** | Recomputed from the released `ddm.csv` with the Shapiro-gated ART / parametric rule: 22 of 24 F values match to three decimals (e.g. PM drift interrupt F = 4.078, interaction F = 6.466, PM noise pre-post F = 12.593, PM non-decision pre-post F = 15.851) and the effect-size column is recovered as partial ω² = df₁(F−1)/(df₁(F−1)+60). **Mismatch:** PM bound interrupt F = 3.221 vs 3.020 and PM bound interaction F = 2.233 vs 2.385. Robustness: recomputing on independently refitted parameters changes every F but keeps the PM conclusions — at the authors' dt = 1e-4 one of 24 significance decisions flips, at dt = 1e-3 four do (see §3 and D6) |
| I9 | Post-hoc contrasts on the PM DDM parameters (Section 4.1.3) | **partial** | The central contrast reproduces — drift, TikTok pre vs post, t(14) = 3.80, p_holm = .020 vs the paper's t = −4.683, p < .001 (sign is the contrast direction). The others do not: TikTok vs Rest / Twitter / YouTube on drift are p_holm = .26 / .15 / .65 here against .002 / < .001 / .014. Blocker: `art.con` (ART-C, Elkin et al.) with emmeans' Kenward-Roger df has no Python equivalent, and the paper does not say which family each Holm correction ran over (its df jump between 56, 91.45, 106.93 and 112) |
| I10 | Pooled TikTok DDM fits behind Figure 6 (Section 4.1.3, Figure 6) | **reproduced** | Accuracy 80.00 % pre / 49.02 % post — exact; fit loss 457.3 vs 457.13 and 461.46 vs 461.46; non-decision time 468 ms vs 461 ms and 681 ms vs 681 ms; post-interruption drift exactly 0.000 as reported; the whole qualitative pattern (drift to zero, variance up, bound down, non-decision time up) holds in every repeat. **Mismatch:** the individual μ, σ and B are not stable run to run, because the optimiser is unseeded and the model is scale-unidentified. Eight repeats give pre μ ∈ [1.21, 1.46], σ ∈ [1.56, 1.88], B ∈ [1.60, 1.93] at losses 457.105–457.192, and separate runs have landed as far out as μ = 0.44, σ = 0.57, B = 0.58 — always on the same ray (μ/σ = 0.774 ± 0.0003, B/σ = 1.02). The published triple 1.46 / 1.89 / 1.94 sits inside that spread, and the run recorded in `results/` landed at 1.48 / 1.92 / 1.95; the same file re-run will report different numbers |
| I11 | One-way ANOVAs on Engagement, SUQ-A, BSMAS (Section 4.2) | **reproduced** | F(3,56) = 2.592 / 2.267 / 1.065, p = .062 / .091 / .371 against the paper's 2.59 / 2.267 / 1.065 and .062 / .091 / .371 |
| I12 | Bayes-factor ANOVAs (Section 4.2) | **reproduced** | BF₀₁ = 1.2131 (SUQ-A) and 3.9030 (BSMAS) against the reported 1.213 and 3.903. **Mismatch:** Engagement BF₀₁ = 0.8856 against 0.893 (−0.8 %). Since the other two match to four digits under the same prior and the same code path, this residual is either a different integration route inside `BayesFactor::anovaBF` for that scale or a reporting slip; the paper names neither the software nor the prior, so it cannot be settled |
| I13 | Figures 3 and 4 (RT distributions; pre/post accuracy) | **reproduced** | Redrawn from the trial data in `results/fig3_rt_ld.png`, `fig3_rt_pm.png`, `fig4_accuracy.png`; the qualitative claims hold — the error-response mass explodes only in the TikTok post-interruption PM panel, LD accuracy is flat across conditions |
| I14 | Figure 5 (fitted DDM parameters, PM task) | **partial** | Redrawn in `results/fig5_ddm_pm.png` and the pre/post pattern matches, but the plotted quantities are the non-identified parameters of I7, and the significance brackets depend on the contrasts of I9 that could not be reproduced |
| I15 | As-run design descriptives against the stated design (Sections 3.2, 3.4) | **partial** | N = 60 with exactly 15 per condition — reproduced. **Mismatch:** every participant has exactly **14** PM cue trials per block, not the 16 stated in Section 3.2, i.e. 28 rather than 32 in total, and 174 rather than the 176 trials Section 3.4 says Task Pre contained. **Second mismatch:** Section 3.2 says stimuli had "a word length ranging from six to eight letters", but 44.7 % of the non-cue strings in `rt.csv` are four or five letters long (range 4–8, mean 5.82). The paper's "PM cue detection accuracy decreased by almost 40%" (Section 5.2) does check out: 39.2 % relative, 31.4 percentage points |
| I16 | Sample descriptives: age, gender, weekly screen time per condition (Section 3.1) | **blocked** | The released data contain no demographic or screen-time variables at all (`q.csv` holds only questionnaire scale scores), and the beginning/ending Google Forms responses were never released. Nothing in Section 3.1 can be checked |

**Derived summary (not comparable across papers or runs):** 9 reproduced, 6 partial, 1 blocked of
16 inner-loop components — 56 % fully reproduced on *this* decomposition. Slice the paper
differently (one row per statistical model, or one per figure, or one per results subsection) and
that percentage moves; the table above, not the percentage, is the result.

---

## 2. The inner/outer boundary

**Outer loop — the human study, not attempted and not scored.**

| Component | Why it is outer |
|---|---|
| Recruitment and sample: 60 fluent German speakers (C2), recruited by university mailing list and social media (Section 3.1) | Requires people; the language requirement is a property of participants, not of the analysis |
| Condition assignment from self-reported platform screen time — participants were assigned to the app they used most, or to Rest (Section 3.1) | The assignment consumes a per-person self-report that only a participant can supply |
| The dual LD + PM session: 160 LD and 16 PM trials per block on a 165 Hz monitor with a masked keyboard, PsychoPy (Sections 3.2, 3.4) | Behavioural data are generated by human key presses under a specific apparatus |
| The 10-minute interruption: participants' own Twitter or TikTok feeds, a chosen YouTube video, or rest without screens (Section 3.3) | The manipulation is personalised, ecologically situated, and happens in third-party apps on the participant's own phone |
| Questionnaires: engagement item, SUQ-A, BSMAS, screen-time reports (Section 3.5) | Self-report from participants |
| Consent, training block, experimenter prompting participants back to the computer (Section 3.4) | An experimenter is in the loop |

**Inner loop — reproduced here.** Everything downstream of the trial table: accuracy derivation,
the mixed models, the DDM fitting, the ANOVAs and their post-hoc contrasts, the Bayes factors and
all four figures. This paper's contribution is empirical rather than technical, so its inner loop
*is* the analysis over the released data — which is exactly why the authors' decision to publish
trial-level data makes so much of it checkable.

Two components sit near the line and were deliberately placed inner: the **DDM fitting** (it is a
mechanical model fit over already-collected RTs, not a measurement of people) and the **as-run
design descriptives** (counting trials in a released file needs no participants). Conversely,
the *stimulus set* is only half recoverable — the strings survive inside `rt.csv`, but the
SUBTLEX-DE frequency matching that produced them (Section 3.2) cannot be checked without the
generation script, which is not released.

---

## 3. Verification runs

Canonical run recorded in `results/` (authors' data, their `ddm.csv` for Table 1, DDM time step
1e-4 for the pooled Figure-6 fits):

```
$ python src/fetch_data.py --dest /tmp/mpm-data
$ python src/analyze.py /tmp/mpm-data/rt.csv --questionnaires /tmp/mpm-data/q.csv \
      --ddm /tmp/mpm-data/ddm.csv --ddm-dt 0.0001 --out results
...
89 quantities within tolerance, 11 outside, of 100 compared
wrote results/results.json and comparison.csv
```

The 11 outside tolerance are: the PM trial count and the stimulus-length range (I15), the LD R²
(I2), the two RT-significance checks (I6), the two PM-bound F values (I8), and four pooled-fit
quantities (I10) — every one of them documented above. Only the I10 rows change from run to run,
because the optimiser is unseeded and the DDM is scale-unidentified; `results/results.json` records
one draw and `results/ddm_stability_runs.json` records eight more. Every other row is stable.

Supporting runs:

```
$ python src/ddm_stability.py /tmp/mpm-data/rt.csv --repeats 8 --dt 0.0001
run 1: pre mu=1.415 sigma=1.829 B=1.866 t=464ms loss=457.11 | post mu=0.000 sigma=2.387 B=1.737 t=682ms loss=461.44
run 2: pre mu=1.459 sigma=1.884 B=1.930 t=461ms loss=457.12 | post mu=0.000 sigma=2.373 B=1.727 t=681ms loss=461.44
run 3: pre mu=1.211 sigma=1.564 B=1.601 t=462ms loss=457.11 | post mu=0.000 sigma=2.420 B=1.758 t=682ms loss=461.45
...  (8 runs; loss range 457.105-457.192 pre, 461.441-461.516 post)
```

Run 2 lands on the published values (1.46 / 1.89 / 1.94 / 461 ms) almost exactly; the others do
not, while fitting the data equally well. Across the 8 runs μ/σ = 0.774 ± 0.0003 and B/σ = 1.023 ±
0.003 — the ratios are pinned, the individual parameters are not.

```
$ python src/analyze.py /tmp/mpm-data/rt.csv --questionnaires /tmp/mpm-data/q.csv \
      --ddm-dt 0.0001 --out results-refit          # 240 fits, 45 min
$ python src/compare_ddm.py /tmp/mpm-data/ddm.csv results-refit/ddm_refit.csv
  drift r=0.894  noise r=0.791  bound r=0.173  nondectime r=0.998
  drift/noise r=0.999   bound/noise r=0.991
```

Recomputing Table 1 on those refitted parameters changes all twenty-four F values. At the authors'
own time step (dt = 1e-4) the PM conclusions survive — drift interruption .011 → .006, drift
interaction .001 → .000, variance interruption .009 → .002, bound interruption .037 → .043 — and
one decision flips: LD drift × interruption .067 → .019, which contradicts "ANOVAs could not find
any significance in all model parameters for the LD task" (Section 4.1.3). At the coarser dt = 1e-3
four flip, including the reported significant PM bound × interruption effect (.037 → .424) and two
further LD nulls. So Table 1's *conclusions* about the PM task are robust to refitting at the
authors' settings, while its individual F values, and the LD null, are not.

---

## 4. Decisions the paper leaves unwritten

| # | Question | Where the paper leaves it open | What was assumed here | Sensitivity |
|---|---|---|---|---|
| D1 | Is a trial a "PM trial" because the stimulus was a cue word, or because the participant pressed a PM key? | Section 4.1.1 defines accuracy only as correct key presses over key presses; Section 3.2 defines the cues but never the labelling rule | Used the released `task` column, which labels by *response*: 79 non-cue trials answered with a PM key are counted as PM errors and 37 cue trials answered with an LD key are counted as LD errors | Re-derived with stimulus-based labelling: PM TikTok-vs-Rest β 0.456 → 0.452, interaction −0.361 → −0.391, all p < .001. Conclusion unchanged |
| D2 | Do trials with no key press count as errors or drop out? | Section 4.1.1's ratio is silent on the 103 no-response trials | Dropped, following the authors' notebook | Counting them as errors: PM β 0.456 → 0.440, all p < .001. Conclusion unchanged |
| D3 | Is the training block excluded from analysis? | Section 3.4 describes training but no exclusion rule; the released file marks 600 training trials | Excluded | Folding the 600 training trials into the pre block: PM Rest β 0.456 → 0.456, pre β 0.314 → 0.318, all p < .001. Conclusion unchanged |
| D4 | What degrees of freedom back the reported Wald t values? | Section 4.1.1 quotes t(114), t(110), t(230) with no df rule | N − p − 2, which reproduces all three exactly | Using N − p instead moves p values in the fourth decimal; no conclusion depends on it |
| D5 | Is the quoted R² marginal or conditional? | Section 4.1.1 quotes a bare "R² = 0.67" for two different models | Conditional (Nakagawa), which matches for the PM model (0.667) and the combined model (0.380) | For the LD model conditional is 0.99 and marginal 0.05 — neither is 0.67, so the LD figure appears to be the PM model's value copied across |
| D6 | Every DDM fitting detail: free parameters, search ranges, loss function, optimiser, dx, dt, seed | Section 3.6 names the four parameters; Section 4.1.3 says only "We used PyDDM to fit responses in the LD and PM tasks per participant" | Taken from the authors' notebook: drift ∈ [0,50], noise ∈ [0.5,4], bound ∈ [0.1,2], non-decision ∈ [0,1], `LossRobustBIC`, differential evolution, dx = 1e-3, T_dur = 3 s, and no seed | **High.** σ is left free, so (μ, σ, B) are identified only up to a common scale: 8 unseeded repeats give μ ∈ [1.21, 1.46] at constant loss, and full refits correlate r = 0.17 with the released bound values. Table 1's PM conclusions survive a refit at the authors' dt = 1e-4 (1 of 24 decisions flips, in the LD task), but not at dt = 1e-3 (4 flip, including the reported PM bound effect) — so the discretisation is load-bearing too. 7 of 120 PM bound estimates sit exactly on the search boundary B = 2 |
| D7 | The normality gate: which test on what, at which α, and which effect size on each branch | Section 4 says "depending on normality, evaluated by the Shapiro-Wilk test ... or ART ANOVAs for the non-parametric data" | Shapiro-Wilk on the whole parameter column, α = .05, ART when p < .05 (partial ω²) and a parametric mixed ANOVA otherwise (partial η²), as in the authors' `stats.R` | Decisive for the LD drift row: Shapiro p = .278 sends it down the parametric branch and reproduces F = 2.520 exactly, while ART would give F = 2.680 |
| D8 | Which Bayes factor, with which prior scale? | Section 4.2 reports BF₀₁ values with no prior, no scale, no software | JZS g-prior with `BayesFactor`'s default rscaleFixed = 0.5, integrated by quadrature | Reproduces two of three values exactly; at the wider scales r = 0.707 and r = 1 the BSMAS BF₀₁ moves from 3.90 to 6.63 and 12.89, and the Engagement BF₀₁ crosses from 0.89 (favouring H1) to 1.24 and 2.04 (favouring H0), so the reported numbers do depend on the unstated default |
| D9 | Which trials enter the RT models, and which model was selected? | Section 4.1.2 gives a formula and says selection was "guided by BIC criteria" | Correct responses only (from the notebook — the paper never says so); the reported Gamma-log model | In the authors' own released comparison the BIC-minimal model is not the reported one (PM: 53.0 for the inverse-Gaussian model against 155.4 for the reported Gamma-log; LD: −7539 against −6099), so the stated criterion does not select the reported model |
| D10 | How are the scales scored? | Section 3.5 says only "according to their original documentation" | SUQ-A as an item mean (released values 1.6–6.8 on a 1–7 scale), BSMAS as a sum (5–18), engagement as a single 1–5 item | Untestable from the released data: only the scored totals are published, not the item responses. The released questionnaire PDF also contains two duplicated items (SUQ-A items 1 and 2 are identical; BSMAS items 6 and 7 are identical), so the number of items actually administered is uncertain |
| D11 | Over which family were the post-hoc p values corrected? | Section 4.1.3 lists contrasts with df of 56, 91.45, 106.93 and 112 without saying which emmeans call each came from | Holm over all ten contrasts per parameter | Large: with a per-parameter family, only the TikTok pre-vs-post drift contrast survives here; a narrower family would let more through |
| D12 | Which measures were collected but not reported? | Sections 3.5 and 4.2 describe engagement, SUQ-A and BSMAS only | Analysed those three | The released `q.csv` also contains `META_CC`, `META_POS`, `META_CSC`, `META_NEG`, `META_NC` — five metacognition subscales that appear in neither the paper nor the released questionnaire PDF, and whose relation to the reported analyses cannot be established |
| D13 | What exactly was pooled for Figure 6? | Section 4.1.3 says "for all 15 participants" without stating the trial filter | All TikTok PM trials with a response, pre and post separately (205 and 204 trials) | Exact: this recovers the published 80.00 % / 49.02 % accuracies and the losses 457.14 / 461.45 |
| D14 | How many YouTube videos were offered, and which? | Section 3.1 says participants chose "one video out of ten options"; Section 3.3 says "a playlist of 10 minute YouTube videos" | Used the released playlist as the ground truth | The released `YT_interruption_Videos_list.txt` lists **11** videos, not ten; video identity and duration are otherwise unrecoverable |

---

## 5. Open-science scorecard

| Criterion | Found | Where |
|---|---|---|
| **Code** | yes | `https://github.com/mimuc/media-prospective-memory` — fetched; 9 notebooks, `stats.py`, `stats.R`, `requirements.txt`, all with stored outputs. Mirrored on `https://osf.io/kzxy7/` |
| **Data** | yes | Same repository, `data/rt.csv` (21,480 trial-level rows), `acc.csv`, `ddm.csv`, `q.csv`; also on OSF. Declared CC-0 in the README |
| **License** | yes | `LICENSE` in the repository is GNU GPL-3.0 (GitHub API confirms `gpl-3.0`); the README declares the *dataset* CC-0 and the *code* GPL-3.0. Note the OSF project sets a single project-wide licence of "GNU General Public License (GPL) 3.0", which does not carry the CC-0 dedication for the data |
| **Preregistration** | **none found** | `api.osf.io/v2/nodes/kzxy7/registrations/` returns 0; an OSF-registries title search for "prospective memory" returns nothing by these authors; no AsPredicted or ClinicalTrials identifier appears in the paper; the paper contains no preregistration statement and no power analysis |
| **Supplementary artifacts** | partial | The questionnaires the paper promises "in the supplementary material" (Section 3.5) are on OSF as `CHI23_Questionnaires.pdf` (fetched), together with `YT_interruption_Videos_list.txt` (fetched) — neither is on GitHub, and the ACM DL supplementary tab could not be reached (HTTP 403). Section 7 claims "our experimental setup ... available on Github", but no PsychoPy program, stimulus-generation script or survey instrument is in the repository |

Ethics: the paper reports informed consent (Section 3.4) but names no ethics board or approval
number, and states no compensation.

---

## 6. What an author could fix cheaply

1. Publish the PsychoPy program and the stimulus lists — Section 7 already promises them.
2. Fix σ (or B) to a constant in the DDM, seed the optimiser, and re-run Table 1; as it stands the
   parameter values are one draw out of many equally good ones.
3. Reconcile Section 4.1.2 with `appendix1`: the released supplement contains two significant RT
   interactions that the paper says do not exist.
4. Correct the LD model's R² (0.99, not 0.67) and the PM trial count (14 per block, not 16).
5. Add the five `META_*` columns to the questionnaire documentation, or remove them from the
   released file.
