# Independent phase-pick review request

Please independently review the four-event SCEDC phase-pick results in this repository.

## Requested review

1. Download the fixed inputs using the URLs and hashes in the bundle.
2. Run the fixed runner without changing thresholds or time windows.
3. Review whether the automatic P/S phase candidates are physically plausible.
4. Record, for each event and station, an independent P/S pick or `UNVERIFIABLE`.
5. Report picker identity or organization, UTC timestamp, software/version, and input/output SHA-256.

Do not use the review to tune the runner. Do not infer a seismic source location from these data alone.

## Acceptance rule

This request is accepted only when an independent reviewer supplies a signed or publicly attributable report with:

- reviewer identity or organization;
- exact commit SHA;
- input hashes;
- independent phase picks or explicit `UNVERIFIABLE` decisions;
- disagreement in seconds for every comparable pick;
- software and environment details;
- output hash.

Until those fields are received, `human_third_party_phase_review` remains `NOT_ESTABLISHED` and `formal_pass` remains `false`.

## Scope boundary

This is a reproducibility and phase-pick review request. It is not a certified earthquake location, hazard assessment, instrument calibration, or claim about causality.
