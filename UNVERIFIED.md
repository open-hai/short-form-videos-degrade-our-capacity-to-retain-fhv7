# Unverified

Everything below is something this audit could not confirm, each with the specific reason.
Nothing here is a criticism of the paper by itself — it is a list of claims that no available
artifact lets anyone check.

## Blocked by missing artifacts

1. **Sample descriptives (Section 3.1).** "35 female, 25 male, aged 19–34, M = 24.80, SD = 3.40",
   "all had a high school education or higher", "fluent German speakers (C2)", "normal or
   corrected-to-normal vision with no history of any neurological or psychiatric disorders".
   *Blocker:* the released data contain no demographic columns; the beginning/ending Google Forms
   responses were never published.

2. **Weekly screen-time figures (Section 3.1).** Rest 2.04 h (SD 3.37), TikTok 5.57 (2.25),
   YouTube 6.75 (2.49), Twitter 5.51 (2.45), plus the per-app figures (TikTok 1 h 46 min, SD .81).
   *Blocker:* no screen-time variable exists in `q.csv` or `rt.csv`. Note that these numbers cannot
   even be sanity-checked: the Rest condition's SD exceeds its mean, and the units of the per-app
   SDs (".81", "1.94", ".52") are not stated.

3. **Condition assignment as executed (Section 3.1).** "Participants were randomly assigned to
   either the app with the highest screen time in the previous week or to Rest."
   *Blocker:* there is no assignment log and no screen-time variable, so neither the randomisation
   nor the claim that each participant got a platform they use frequently can be checked. The
   procedure also means platform conditions are self-selected populations; the paper acknowledges
   this in Section 5.1 but the data cannot settle it.

4. **Apparatus and counterbalancing (Section 3.2).** The Acer Predator XB241YU at 165 Hz, the
   masked keyboard, and "We counterbalanced the key-response mapping across participants".
   *Blocker:* `rt.csv` records no key-mapping variable, so counterbalancing cannot be verified;
   the PsychoPy program that would encode it is not released.

5. **Stimulus construction (Section 3.2).** "Word stimuli were extracted from the SUBTLEX-DE
   database", "Psycholinguistic properties, such as the mean length and frequency, were matched
   across experimental sessions", "Non-words were pseudo-word stimuli created from the used words
   by changing one or two letters."
   *Blocker:* the generation script and the word list are not released, and `rt.csv` does not mark
   which strings are words and which are pseudo-words, so frequency matching cannot be checked.
   What *can* be checked contradicts the text: string lengths run 4–8 letters, not 6–8
   (44.7 % of non-cue trials are shorter than six letters).

6. **Trial timing (Section 3.2).** Fixation cross of 1250/1500/1750 ms, 3000 ms stimulus limit,
   1000 ms inter-stimulus interval, at least 10 LD trials before the first PM cue and at least 8
   between cues.
   *Blocker:* `rt.csv` has no timestamps or trial indices, so neither the timing nor the cue
   spacing constraint can be verified. The 3000 ms limit is at least consistent with the data: the
   longest recorded RT is 2.96 s.

7. **Interruption compliance (Section 3.3).** That participants actually scrolled their own feed,
   watched a single video, or refrained from screens for the full 10 minutes.
   *Blocker:* no interruption logs, screen recordings or app telemetry were collected or released.

8. **Ethics.** The paper reports informed consent (Section 3.4) but names no review board,
   approval number, or compensation. *Blocker:* nothing to check against.

## Blocked by inaccessible venues

9. **ACM Digital Library supplementary material and any artifact badges.** Section 3.5 says "The
   questionnaires are included in the supplementary material". *Blocker:* every automated request
   to `dl.acm.org` returned HTTP 403 behind a Cloudflare interstitial. The questionnaire PDF was
   instead found on OSF, so the claim is satisfied somewhere — but whether the ACM record carries
   it, and whether the paper holds any reproducibility badge, is unverified here.

10. **Whether the published ACM version differs from the author PDF.** The audit used the arXiv
    and author-hosted PDFs (identical to each other in the sections used). *Blocker:* the ACM PDF
    could not be retrieved. One visible discrepancy: the paper's own ACM reference format block
    says "14 pages", while the GitHub README and the ACM DL landing page say 15.

## Method claims that cannot be reconciled

11. **"a GLMM using REML" (Section 4.1.2).** `glmer` does not fit generalised models by REML, and
    the authors' own released notebook prints "refitting model(s) with ML (instead of REML)". The
    estimator actually used for the RT models is therefore ML, not REML as stated.

12. **Model selection "guided by BIC criteria" (Section 4.1.2).** In the released comparison the
    BIC-minimal model is not the model the paper reports (PM: BIC 53.0 for the inverse-Gaussian
    model against 155.4 for the reported Gamma-log; LD: −7539 against −6099). Which criterion
    actually selected the reported model is unclear.

13. **The post-hoc contrast families (Section 4.1.3).** The reported degrees of freedom vary
    across contrasts (56, 91.45, 106.93, 112) without any statement of which `emmeans` call
    produced each, so the Holm correction's family cannot be reconstructed. It is also unexplained
    why σ_PM is reported significant pre-vs-post for *Twitter* and t_PM for *YouTube* while
    Figure 5 marks the TikTok column — this audit's own contrasts find the TikTok pre-vs-post
    difference on σ (p_holm = .035) and not the Twitter one.

14. **The two PM-bound rows of Table 1.** Recomputing from the released `ddm.csv` reproduces 22 of
    24 F values exactly but gives 3.221 (paper: 3.020) and 2.233 (paper: 2.385). Seven of the 120
    PM bound estimates sit exactly on the fitting boundary B = 2, which produces ties in the
    aligned ranks; whether ARTool's mixed-model alignment handles those differently, or whether
    the published row came from a different fit of the DDM, cannot be determined without rerunning
    ARTool itself (R is not available in this environment).

15. **The `META_*` columns.** `q.csv` contains `META_CC`, `META_POS`, `META_CSC`, `META_NEG`,
    `META_NC` — five subscale scores that look like a metacognition questionnaire (MCQ-30). They
    appear in no section of the paper and in no released questionnaire. Whether they were
    collected as an unreported measure, or are left over from another study, is unknown.

16. **Duplicated questionnaire items.** In `CHI23_Questionnaires.pdf`, SUQ-A items 1 and 2 have
    identical text, and BSMAS items 6 and 7 have identical text. Whether participants saw a
    duplicated item or the PDF is a transcription slip cannot be resolved, and it leaves the number
    of items actually scored uncertain.

## Method gaps of my own re-implementation

17. **lme4 vs statsmodels.** All accuracy LMMs were refitted with `statsmodels.MixedLM`, which
    reproduces every reported β, CI and t. Small differences in the third decimal of β are
    expected and observed (≤ 0.005) and are not evidence about the paper.

18. **No Gamma GLMM, no crossed-random-effects binomial GLMM in Python.** The RT and trial-level
    accuracy models here are a log-normal LMM and a variational-Bayes binomial GLMM. They agree
    closely with the authors' released lme4 output, but they are not the same estimator.

19. **No ART-C.** The post-hoc contrasts use pairwise tests on the same aligned ranks with Holm
    correction, not ARTool's ART-C with Kenward-Roger degrees of freedom.

20. **DDM refits.** The 240-cell refits reported here were run twice: once at the authors' own
    dt = 1e-4 and once at dt = 1e-3, both with dx = 1e-3 and their other settings. Whether an
    exhaustive search with many restarts would converge on their published per-cell values cannot
    be settled, because the model is scale-unidentified in the first place: any (μ, σ, B) on the
    same ray fits equally well, so "the" published values are not a target a refit can hit.
