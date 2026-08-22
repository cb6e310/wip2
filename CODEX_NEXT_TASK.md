# Waiting for stimulus grouping policy review

Active SPEC: `guide/NC_HSG_Paper_Spec_v1_8_2026-08-22.md` (version `v1.8`).

Run 009 completed the bounded source binding and all-pair similarity diagnostic. The sole READY and recommended task is:

```text
S0_STIMULUS_GROUP_POLICY_REVIEW
owner: CHATGPT_OR_AUTHOR
status: READY
```

Review the committed score distributions, broad-prefilter candidates, trigger intersections, top opaque pairs, and component-risk summaries. Freeze a versioned final threshold and grouping policy, or explicitly reject grouping, before authorizing implementation.

Codex must stop here. Do not infer paraphrases from high similarity, select a threshold from the observed distribution, emit `near_duplicate_group_id`, merge exact occurrences, construct a split, read EEG or outcomes, select backbone A, train, or run a Gate. `S0_STIMULUS_ID` and `S0_JOINT_SPLIT` remain BLOCKED.
