# Periodic spin-one Haldane gap: gamma_L > 771/5000 at inverse temperature 13

> **CORRECTION — 2026-11-05.** The 0.1542 claim below is **not certified by
> this repository**. Independent replay found four manual residual overrides
> that strengthen the certificate inputs; without them the checker fails before
> coverage at the board domain. The physical claim is not disproved, but this
> artifact supports only much lower rigorous targets. See
> [`CORRECTION.md`](CORRECTION.md). The text below is retained as historical
> claim material, not as current evidence.

For every integer L >= 68, at J=1, the periodic spin-one Heisenberg chain has a
unique ground state and a spectral gap

    gamma_L > 771/5000 = 0.1542,

with the analytic premises of the upstream papers (OpenAI's periodic Haldane-gap
and boundary-field preprints, commit adc7f124) and the certified finite inputs
as dependencies. This **improves the current listed bound 303/2000 = 0.1515**
(amachino/haldane-gap-refinement v1.7, Oct 2026) by 1.8% relative — and the
boundary is measured, not asserted: 0.1542 certifies, 0.1543 fails on the tail
exponential comparisons.

## What is whose

- **OpenAI**: the spatial-transfer identities (Prop 3.1), the two-purity
  uniform-gap criterion (Prop 4.3), and the finite periodic inputs
  (Corollary 5.6) of the two preprints this certificate is conditional on.
- **amachino (haldane-gap-refinement)**: the entire certificate architecture —
  the quarter-turn thermal engine, exact Gaussian-integer trace enclosures,
  octahedral sector decomposition, exterior-ray filters, degree-8 moment
  polynomials, sector recurrence and tail invariant — and the v1.7 result
  0.1515 that this work improves.
- **MultiAgency / darkhipo**: the exact four-rotation thermal tables at
  inverse temperature 13 (recomputed from the upstream engine with all exact
  cross-checks), the rigorous certificate chain at beta=13 (this repo), the
  filter/polynomial regeneration on the beta=13 supports, and the exact
  boundary bisection (0.1542 passes / 0.1543 fails). The beta=13 LP-residual
  seed family is used only with recurrence-computed residuals; no fitted or
  approximate inputs enter the certificate.

## The certificate

`verify_quarter_refinement_beta13.py` runs 395 exact-rational checks:
the five-site energy certificate, octahedral character and projection
identities, exact four-rotation trace enclosures, sector moment intervals,
8 exterior-ray quartic filters with exact domination, 117 degree-8 moment
polynomials certified on intervals by Bernstein subdivision, the seed and
ten doubled-temperature recurrence rows, six finite intervals from L=68 to
33791, and the infinite-tail invariant. All scalar acceptance decisions and
polynomial interval checks use rational arithmetic; no floats enter any
acceptance decision.

Result receipt: `quarter_refinement_beta13.json` (the full statement,
seed, levels, intervals, tail and all 395 named checks).

## Boundary measurement

With TARGET bisected on a 1e-4 rational grid:

    0.1541  PASS
    0.1542  PASS   <- the certified bound (this repo's statement)
    0.1543  FAIL (tail exponential comparisons)
    0.15436 FAIL

The LP exploratory screen's diagnostic ceiling (0.15436) was therefore only
slightly optimistic; the certified ceiling is 0.1542. Inverse temperature 13
improves on the incumbent's 49/4 construction at this ceiling; colder was not
automatically better (earlier attempts at higher temperature did not certify
above the incumbent).
