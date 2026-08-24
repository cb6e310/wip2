# Codex Next Task - S0_A_INTERFACE

## Current state

Run 012 activated RC-HSG v2.1 and materialized the author-frozen
`RC_HSG_NATIVE_SPECTRAL_A1_V1` policy. `S0_A_INTERFACE` is the sole READY and
recommended task, owned by `CODEX`.

## Required next instruction

Wait for an exact execution directive for `S0_A_INTERFACE`. That future run may
implement and freeze only the project-native spectral frontend tensor,
masking, deterministic initialization, and outer-train-only admission contract
specified by active SPEC section 20.10 and `artifacts/backbone_a_policy.yaml`.

## Frozen boundary

- Input: finite 105 x T release-native EEG at 500 Hz in the frozen channel
  order and common-average processed reference.
- No physical-unit conversion, microvolt inference, channel interpolation,
  external source-code copy, pretrained checkpoint, or weight download.
- Segments shorter than 500 valid samples fail admission; silent padding is
  prohibited.
- N1, N2, real, and all comparison methods must eventually share one frontend
  path.

## Hard stop

Do not implement `S0_A_INTERFACE` without the next exact directive. Do not
implement F, semantic schema, candidate selection, reference generation,
reliability models, GLMs, calibration, or later methods. Do not read real EEG
values, semantic outcomes, calibration/test results, predictions, or historical
model metrics. Do not run the full leakage audit, train, execute any Gate, or
unlock test.
