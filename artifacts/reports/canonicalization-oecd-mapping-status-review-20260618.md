# OECD mapping-status review

Artifact: `canonicalization-oecd-mapping-status-review-20260618`  
Created UTC: `2026-06-18T22:30:01Z`  
Scope: bounded review artifact only.

## Conclusion

Existing OECD GDP unit-basis evidence supports **continued deferral today** and a **future path toward separate basis-specific provisional treatments**. It does **not** support approving either OECD mapping now.

TASK-040 satisfied the precondition that OECD `USD_EXC` and `USD_PPP` must be distinguished. That distinction is necessary, but not sufficient, for mapping advancement. The missing piece remains a review-approved policy for exchange-rate-vs-PPP treatment, report eligibility, and caveat/state representation.

## Treatment review

### `USD_EXC` — exchange-rate current USD

- Current evidence status: basis distinguished by TASK-040.
- Review conclusion: remain deferred.
- Future candidate: separate governed provisional exchange-rate USD treatment.
- Current report eligibility: not eligible for comparable GDP reports.
- Reason: no review-approved report policy says OECD exchange-rate current-USD values can enter comparable GDP outputs alongside WDI/current-USD evidence.

Minimum future evidence required:

1. Review-approved exchange-rate basis policy for OECD `B1GQ`.
2. Stable evidence link for `USD_EXC` unit metadata interpretation.
3. Explicit report-impact decision preserving no-conversion/no-aggregation boundaries.
4. State/manifest deltas only after review approval; no direct base-state mutation.

### `USD_PPP` — PPP current USD

- Current evidence status: basis distinguished by TASK-040.
- Review conclusion: remain deferred.
- Future candidate: separate governed provisional PPP USD treatment.
- Current report eligibility: not eligible for current-USD exchange-rate GDP reports.
- Reason: PPP-basis GDP differs materially from exchange-rate current-USD GDP and requires a separate report treatment/profile or explicit exclusion.

Minimum future evidence required:

1. Review-approved PPP basis policy for OECD `B1GQ`.
2. Stable evidence link for `USD_PPP` unit metadata interpretation.
3. Explicit decision on PPP-specific report eligibility versus continued exclusion.
4. State/manifest deltas only after review approval; no direct base-state mutation.

## Comparability implications

- The evidence supports separating comparability profiles, not collapsing OECD `B1GQ` into one generic GDP mapping.
- `USD_EXC` and `USD_PPP` must remain disjoint comparability groups unless a later policy explicitly models their relationship.
- `USD_EXC` may be closer to WDI current-USD metadata than `USD_PPP`, but that is not enough to prove report-safe comparability.
- `USD_PPP` may be analytically useful, but it should not be mixed into exchange-rate/current-USD GDP outputs.

## Report eligibility implications

No OECD `B1GQ` basis candidate is eligible for report integration from this review alone.

- `USD_EXC`: possible future exchange-rate/current-USD report eligibility after policy review.
- `USD_PPP`: possible future PPP-specific report/profile, otherwise continued exclusion from exchange-rate GDP reports.
- Existing GDP reports remain unchanged.

## Remaining uncertainty

- Whether MacroForge should treat OECD `USD_EXC` as provisionally comparable to WDI current-USD evidence.
- Whether MacroForge should create or defer a separate PPP GDP analytical/report treatment.
- How accepted/provisional state should encode basis caveats so downstream reports cannot accidentally mix bases.
- Whether additional OECD unit metadata evidence is needed before a review decision can safely advance either candidate.

## Checks

- usd_exc_evaluated: pass
- usd_ppp_evaluated: pass
- basis_profiles_remain_separate: pass
- supports_future_separate_treatment_path_without_current_approval: pass
- no_mapping_approval_claimed: pass
- no_accepted_state_mutation: pass
- no_manifest_mutation: pass
- no_conversion_or_aggregation: pass
- no_report_integration: pass
- minimum_future_evidence_recorded: pass

## Inputs

- `artifacts/reports/canonicalization-deferred-mapping-advancement-requirements-20260618.json` — sha256 `0b3c4b09bad8cced64f95305a696bc748c92756e69e58ada32bf8d2d049266d8`
- `artifacts/reports/canonicalization-deferred-mapping-advancement-requirements-20260618.md` — sha256 `796937b77c4689a94acf4b0d47912972edb192cd909edd85b9ccb0d99c65bd7c`
- `artifacts/reports/canonicalization-oecd-unit-basis-comparability-20260618.json` — sha256 `806c1c6e141b0b6d6ed52583fe712f501398107ce941125eb8f5cba8dbfd7937`
- `artifacts/reports/canonicalization-oecd-unit-basis-comparability-20260618.md` — sha256 `2302557032b46c166d8d6ab15002254f5ec4b9b7d2ee50ed33154fbb105ce5fc`
- `artifacts/decisions/DEC-018-minimal-ai-assisted-canonicalization-layer.md` — sha256 `04618aebd3cb7055b60dd5196e2df4a9d073372ae3e8e5d33fbbdf88f9c30151`
- `artifacts/tasks/TASK-038-simulate-bounded-canonicalization-review-lifecycle.md` — sha256 `ea3c53139beeed0c9f146d268c2278600b2973771ca94894252cab8a2ba4ac76`
- `artifacts/reports/canonicalization-review-lifecycle-20260614.json` — sha256 `34b2b8882677478b92904fb64e5bed559f49970f008725fef49346ef63509f16`

## Recommended next action

Create a future, separate review-decision task only if MacroForge is ready to choose basis-specific report eligibility policy. Otherwise keep OECD `B1GQ` deferred with the two basis candidates available for future consultation.
