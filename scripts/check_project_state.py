#!/usr/bin/env python3
"""Validate the RC-HSG file-based project memory system.

The validator deliberately fails closed: a task cannot claim readiness or
completion without its declared prerequisites, evidence, run record, and gate
ordering.  Scientific unknowns remain blockers rather than inferred facts.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable

try:
    import yaml
except ImportError as exc:  # pragma: no cover - environment failure
    raise SystemExit("DEPENDENCY_MISSING: PyYAML>=6,<7 is required") from exc


ALLOWED_STATUSES = {
    "TODO",
    "READY",
    "IN_PROGRESS",
    "DONE",
    "BLOCKED",
    "FAILED",
    "SKIPPED",
    "TERMINATED",
}
ALLOWED_GATE_OUTCOMES = {
    None,
    "PASS",
    "FAIL",
    "DEGRADED",
    "TOPIC_ONLY",
    "FAIL_NO_PRIMARY_REFERENCE",
}
ALLOWED_LOCKED_ROUTES = {
    "RC_HSG",
    "ORDINARY_HIERARCHICAL_SELECTIVE_GENERATION",
    "FLAT_RC",
    "RELIABILITY_REFERENCE_STUDY",
    "EMPIRICAL_RISK_AWARE",
}
REQUIRED_TASK_FIELDS = {
    "title",
    "stage",
    "status",
    "prerequisites",
    "produces",
    "acceptance",
}
REQUIRED_TASK_IDS = {
    "SPEC_V27_REVIEW",
    "SPEC_V28_REVIEW",
    "SPEC_V26_REVIEW",
    "SPEC_V25_REVIEW",
    "SPEC_V24_REVIEW",
    "SPEC_V23_REVIEW",
    "SPEC_V22_REVIEW",
    "SPEC_V21_REVIEW",
    "S0_SCIENTIFIC_REDESIGN_FREEZE",
    "SPEC_V20_REVIEW",
    "SPEC_V19_REVIEW",
    "SPEC_V18_REVIEW",
    "S0_STIMULUS_SOURCE_BINDING",
    "S0_STIMULUS_SIMILARITY_DIAGNOSTIC",
    "S0_STIMULUS_GROUP_POLICY_REVIEW",
    "SPEC_V17_REVIEW",
    "S0_DATA_ADMISSION_POLICY_REPAIR",
    "SPEC_V16_REVIEW",
    "S0_ZUCO2_NR_SEGMENT_CORRESPONDENCE",
    "SPEC_V15_REVIEW",
    "S0_ZUCO2_NR_ADMISSION_REPAIR",
    "SPEC_V14_REVIEW",
    "S0_ACTIVE_SPEC_GUARD",
    "S0_ZUCO2_NR_TARGETED_ADMISSION",
    "SPEC_V13_REVIEW",
    "S0_GOVERNANCE_HARDENING",
    "S0_INPUT_DISCOVERY_AUDIT",
    "SPEC_V12_REVIEW",
    "S0_GOVERNANCE_BOOTSTRAP",
    "S0_REPOSITORY_AUDIT",
    "S0_DATA_CARD",
    "S0_SEMANTIC_ITEM",
    "S0_H_DEFINITION",
    "S0_JOINT_SPLIT",
    "S0_LEAKAGE_AUDIT",
    "S0_METHOD_LEAKAGE_AUDIT",
    "S0_A_INTERFACE",
    "S0_A1_FRONTEND",
    "S0_A1_ADMISSION",
    "S0_A3_CONTAMINATION_CHECK",
    "S0_N1_BLOCK_FEASIBILITY",
    "S0_N1_SAMPLER",
    "S0_N2_SAMPLER",
    "GATE_A1",
    "S0_SCHEMA_AUDIT",
    "S0_GATE_A_POPULATION_E5",
    "S0_A_POLICY_REVIEW",
    "STAGE1_PROBES",
    "SHAM_VALIDATION",
    "GATE_A",
    "S0_CALIBRATION_CONTRACT",
    "S0_DIRECT_C",
    "S0_PMI_BASELINE",
    "S0_NC_HSG_CORE",
    "S0_ANMA_ORIG",
    "S0_ALIGN_UNIT_COST",
    "GATE_B",
    "ROUTE_LOCK",
    "MAIN_EXPERIMENT",
    "GATE_R0",
    "S0_REFERENCE_FEATURES",
    "S0_RELIABILITY_MODELS",
    "S0_CALIBRATION_FEASIBILITY_REVIEW",
    "S0_ABSOLUTE_HSG",
    "S0_RC_HSG_CORE",
    "S0_FLAT_RC",
    "GATE_R",
    "GATE_C",
    "GATE_H",
    "MECHANISM_A",
}
V21_ACTIVE_GATES = {
    "gate_r0": "GATE_R0",
    "gate_r": "GATE_R",
    "gate_c": "GATE_C",
    "gate_h": "GATE_H",
    "mechanism_a": "MECHANISM_A",
}
V21_SUPERSEDED_TASKS = {
    "GATE_A1",
    "GATE_A",
    "GATE_B",
    "S0_NC_HSG_CORE",
    "S0_DIRECT_C",
    "STAGE1_PROBES",
    "SHAM_VALIDATION",
}
V21_DEPENDENCIES = {
    "S0_A_INTERFACE": {
        "S0_REPOSITORY_AUDIT",
        "S0_DATA_CARD",
        "S0_A_POLICY_REVIEW",
        "S0_JOINT_SPLIT",
    },
    "S0_SEMANTIC_ITEM": {
        "S0_A_INTERFACE",
        "S0_DATA_CARD",
        "S0_JOINT_SPLIT",
        "S0_LEAKAGE_AUDIT",
    },
    "S0_H_DEFINITION": {"S0_SEMANTIC_ITEM", "S0_JOINT_SPLIT"},
    "S0_SCHEMA_AUDIT": {"S0_SEMANTIC_ITEM", "S0_H_DEFINITION"},
    "GATE_R0": {
        "S0_LEAKAGE_AUDIT",
        "S0_A1_ADMISSION",
        "S0_N1_SAMPLER",
        "S0_N2_SAMPLER",
    },
    "S0_CALIBRATION_CONTRACT": {
        "S0_CALIBRATION_FEASIBILITY_REVIEW",
        "S0_RELIABILITY_MODELS",
        "S0_GATE_A_POPULATION_E5",
    },
    "S0_PMI_BASELINE": {
        "S0_A_INTERFACE",
        "S0_H_DEFINITION",
        "S0_RELIABILITY_MODELS",
        "S0_CALIBRATION_CONTRACT",
    },
    "ROUTE_LOCK": {
        "S0_ABSOLUTE_HSG",
        "S0_RC_HSG_CORE",
        "S0_FLAT_RC",
        "S0_PMI_BASELINE",
        "S0_CALIBRATION_CONTRACT",
        "S0_LEAKAGE_AUDIT",
        "S0_ALIGN_UNIT_COST",
    },
    "GATE_R": {"ROUTE_LOCK", "S0_ABSOLUTE_HSG", "S0_RC_HSG_CORE"},
    "GATE_C": {"ROUTE_LOCK", "S0_RC_HSG_CORE", "S0_CALIBRATION_CONTRACT"},
    "GATE_H": {"ROUTE_LOCK", "S0_RC_HSG_CORE", "S0_FLAT_RC"},
    "MECHANISM_A": {
        "ROUTE_LOCK",
        "GATE_R0",
        "S0_REFERENCE_FEATURES",
        "S0_GATE_A_POPULATION_E5",
    },
    "MAIN_EXPERIMENT": {
        "ROUTE_LOCK",
        "GATE_R",
        "GATE_C",
        "GATE_H",
        "MECHANISM_A",
        "S0_LEAKAGE_AUDIT",
        "S0_ALIGN_UNIT_COST",
    },
}
V22_DEPENDENCIES = {
    **V21_DEPENDENCIES,
    "S0_A_INTERFACE": {
        "SPEC_V22_REVIEW",
        "S0_REPOSITORY_AUDIT",
        "S0_DATA_CARD",
        "S0_A_POLICY_REVIEW",
        "S0_JOINT_SPLIT",
    },
    "S0_LEAKAGE_AUDIT": {"S0_A1_FRONTEND", "S0_JOINT_SPLIT"},
}
V22_OUTPUT_HASHES = {
    "artifacts/backbone_a_contract.yaml": "4c9ccddf4d5c208870422c7e5ceee65ee184d812fce662bb885998b0dad65cac",
    "artifacts/a_interface_eligibility_v1.jsonl": "8eded8fb2786747e96b8388d4d91315e39db9f8a9eb25ea69056d219e1e8e1ad",
    "reports/a_interface_contract.md": "925af0e2ccc95fb01c8479beac8901632ddfd4c180682af0e4f3b0a886133295",
}
V22_B8_BLOCKS = {
    "S0_LEAKAGE_AUDIT",
    "S0_A1_ADMISSION",
    "S0_A3_CONTAMINATION_CHECK",
    "S0_N1_BLOCK_FEASIBILITY",
    "S0_N1_SAMPLER",
    "S0_N2_SAMPLER",
    "GATE_R0",
    "S0_REFERENCE_FEATURES",
    "S0_RELIABILITY_MODELS",
    "S0_ABSOLUTE_HSG",
    "S0_RC_HSG_CORE",
    "S0_FLAT_RC",
}
V23_DEPENDENCIES = {
    **V22_DEPENDENCIES,
    "S0_METHOD_LEAKAGE_AUDIT": {
        "S0_A1_ADMISSION",
        "S0_SCHEMA_AUDIT",
        "S0_REFERENCE_FEATURES",
        "S0_RELIABILITY_MODELS",
        "S0_CALIBRATION_CONTRACT",
        "S0_ABSOLUTE_HSG",
        "S0_RC_HSG_CORE",
        "S0_FLAT_RC",
        "S0_PMI_BASELINE",
    },
    "ROUTE_LOCK": {
        "S0_ABSOLUTE_HSG",
        "S0_RC_HSG_CORE",
        "S0_FLAT_RC",
        "S0_PMI_BASELINE",
        "S0_CALIBRATION_CONTRACT",
        "S0_METHOD_LEAKAGE_AUDIT",
        "S0_ALIGN_UNIT_COST",
    },
    "MAIN_EXPERIMENT": {
        "ROUTE_LOCK",
        "GATE_R",
        "GATE_C",
        "GATE_H",
        "MECHANISM_A",
        "S0_METHOD_LEAKAGE_AUDIT",
        "S0_ALIGN_UNIT_COST",
    },
}
V23_B9_BLOCKS = {
    "S0_A3_CONTAMINATION_CHECK",
    "S0_N1_BLOCK_FEASIBILITY",
    "S0_N1_SAMPLER",
    "S0_N2_SAMPLER",
    "GATE_R0",
    "S0_REFERENCE_FEATURES",
    "S0_RELIABILITY_MODELS",
    "S0_ABSOLUTE_HSG",
    "S0_RC_HSG_CORE",
    "S0_FLAT_RC",
}
V23_OUTPUT_HASHES = {
    "artifacts/a1_frontend_audit_panel_v1.jsonl": "95db4e18501ae25f559bb6446621b6c062a7f36936ca0f4eec3236dc57ca43ed",
    "artifacts/a1_frontend_freeze.yaml": "817b1be11d3545f1279e87fd40d391b71dd3347d0eed57c174abdfc6bf760d66",
    "reports/a1_frontend_selfcheck.md": "703e999bc9903183dd019df853e92558a81ba8526945e32a24ae926d95af4503",
}
V24_OUTPUT_HASHES = {
    "artifacts/a_path_leakage_assertions.yaml": "eb60565b40991f19856673acc030ec7a7dcab6c520c6af5c1b1c39167f864f70",
    "reports/a_path_leakage_audit.md": "491986e4caed53623069b26918b9be232aff74416c8e4ef973955a6810b7fd27",
}
V25_FIXED_INPUT_HASHES = {
    "guide/RC_HSG_Paper_Spec_v2_4_2026-08-24.md": "5878fa84db5abb380c71e6257a4a7c30e0587ab8d505ba0d9446c110d47426b5",
    "artifacts/backbone_a_policy.yaml": "034a523119f12f648266d94e0499179882fbe181584d10c1af17a3502a797425",
    "artifacts/backbone_a_contract.yaml": "4c9ccddf4d5c208870422c7e5ceee65ee184d812fce662bb885998b0dad65cac",
    "artifacts/a_interface_eligibility_v1.jsonl": "8eded8fb2786747e96b8388d4d91315e39db9f8a9eb25ea69056d219e1e8e1ad",
    "src/rc_hsg/backbones/native_spectral_a1.py": "71ae12d65cc0acc6fd5870434e141ee7d849eb8befa718a84fb99cb86ed533d9",
    "artifacts/admission/zuco2_nr_analysis_view_v1.jsonl": "0751259f9f9455cba72bd7d027ffa1423e790e631ac0f5174c38da65d7cd12ff",
    "artifacts/split_regimeI.json": "e2c065e5b395053cd655670fede8a2b117f6eb9821af884ca31c6fed3842fbab",
    "artifacts/data_card.yaml": "d9331bfe34937c264b7b8c667a2b831569c4440120e1d445011aeaf419c30f84",
    "artifacts/admission/zuco2_nr_targeted_manifest_v3.yaml": "50806a60937b28ae36207509c44d606af6f6b6b1be2a69c06081672f0931bfaf",
    "artifacts/admission/zuco2_osf_file_metadata.yaml": "85a8c89eeb7a523c06fb7f38aa1c371e042413087e66dcc338c16833bd8bb721",
    "requirements-trust-align.lock.txt": "72a2a3274ef9516dba95a4f4022cacfba0e02d10445e1618da2a569f59381910",
    "scripts/validate_a1_frontend.py": "ecc84a0363629e919409321cdc73327b6e3c7e779e224a18ab55a6b6ac6777cd",
    "artifacts/a1_frontend_audit_panel_v1.jsonl": "95db4e18501ae25f559bb6446621b6c062a7f36936ca0f4eec3236dc57ca43ed",
    "artifacts/a1_frontend_freeze.yaml": "817b1be11d3545f1279e87fd40d391b71dd3347d0eed57c174abdfc6bf760d66",
    "reports/a1_frontend_selfcheck.md": "703e999bc9903183dd019df853e92558a81ba8526945e32a24ae926d95af4503",
    "scripts/audit_a_path_leakage.py": "797618af0113a2f8f357ea8c91f53de7b9375afcbb3860baf437ebc1bfbe5e24",
    "artifacts/a_path_leakage_assertions.yaml": "eb60565b40991f19856673acc030ec7a7dcab6c520c6af5c1b1c39167f864f70",
    "reports/a_path_leakage_audit.md": "491986e4caed53623069b26918b9be232aff74416c8e4ef973955a6810b7fd27",
    "runs/2026-08-24_015_a_path_leakage_audit.md": "52ff87aad5c260d6bb3ef34367839cbb6f1251ff6f4f1282075db9d4af1b22f6",
}
V25_OUTPUT_HASHES = {
    "artifacts/a1_outer_train_admission_v1.jsonl": "b3c1b4e11855ef4c51c5bd0c2c0009f8a24e390c511d97118c48082fc7febfd5",
    "artifacts/a1_outer_train_admission_freeze.yaml": "e973fbbe841a47f027cbf0f8a8ad65e66d106d675e8ed838dd0daf4a08dcab12",
    "reports/a1_admission.md": "c2dc97d886d31fdc93e82778981fdf3a2dc1fd382c850d4035fdba3487513eac",
}
V25_ADMISSION_CODE_HASH = "6ce68ad66e8fdc51224d3723054ca01b0b13b558d9d6e81932e6e3b6636a8795"
V26_FIXED_INPUT_HASHES = {
    "guide/RC_HSG_Paper_Spec_v2_5_2026-08-24.md": "b225a1528a05d2c0b83b31114347cd045ccc5b9a746df1ae6f06241d976b55ae",
    "artifacts/backbone_a_policy.yaml": "034a523119f12f648266d94e0499179882fbe181584d10c1af17a3502a797425",
    "artifacts/backbone_a_contract.yaml": "4c9ccddf4d5c208870422c7e5ceee65ee184d812fce662bb885998b0dad65cac",
    "artifacts/a_interface_eligibility_v1.jsonl": "8eded8fb2786747e96b8388d4d91315e39db9f8a9eb25ea69056d219e1e8e1ad",
    "src/rc_hsg/backbones/native_spectral_a1.py": "71ae12d65cc0acc6fd5870434e141ee7d849eb8befa718a84fb99cb86ed533d9",
    "artifacts/admission/zuco2_nr_analysis_view_v1.jsonl": "0751259f9f9455cba72bd7d027ffa1423e790e631ac0f5174c38da65d7cd12ff",
    "artifacts/split_regimeI.json": "e2c065e5b395053cd655670fede8a2b117f6eb9821af884ca31c6fed3842fbab",
    "artifacts/admission/zuco2_nr_targeted_manifest_v3.yaml": "50806a60937b28ae36207509c44d606af6f6b6b1be2a69c06081672f0931bfaf",
    "artifacts/admission/zuco2_osf_file_metadata.yaml": "85a8c89eeb7a523c06fb7f38aa1c371e042413087e66dcc338c16833bd8bb721",
    "requirements-trust-align.lock.txt": "72a2a3274ef9516dba95a4f4022cacfba0e02d10445e1618da2a569f59381910",
    "scripts/validate_a1_frontend.py": "ecc84a0363629e919409321cdc73327b6e3c7e779e224a18ab55a6b6ac6777cd",
    "artifacts/a1_outer_train_admission_v1.jsonl": "b3c1b4e11855ef4c51c5bd0c2c0009f8a24e390c511d97118c48082fc7febfd5",
    "artifacts/a1_outer_train_admission_freeze.yaml": "e973fbbe841a47f027cbf0f8a8ad65e66d106d675e8ed838dd0daf4a08dcab12",
    "reports/a1_admission.md": "c2dc97d886d31fdc93e82778981fdf3a2dc1fd382c850d4035fdba3487513eac",
    "runs/2026-08-24_016_a1_full_outer_train_admission.md": "42a0030551fbff4a9c8dd256d786987f620147712556034d2edb6108f5af96dc",
    "artifacts/a_path_leakage_assertions.yaml": "eb60565b40991f19856673acc030ec7a7dcab6c520c6af5c1b1c39167f864f70",
    "guide/RC_HSG_Paper_Spec_v2_6_2026-08-24.md": "174f0ee08870cc045a75336d3fc7138c97a99e78e5adfb109aed74b5c5144aaa",
    "artifacts/spec_review/rc_hsg_v26_n1_block_feasibility_review.md": "b44e0a97c57d8e51e3e8365c56781c88b37328acc28d21f40f070e876d421e87",
}
V26_OUTPUT_HASHES = {
    "artifacts/nulls/n1_block_assignment_v1.jsonl": "d0acc5e5fe78bc36a69cb04b6f605983c675e49a764538ae1665f86a28acee04",
    "artifacts/nulls/n1_block_feasibility.yaml": "90a6178100f507299e12223d15291699aad84e4b58bb52e29843dbf99ee6f771",
    "reports/n1_block_feasibility.md": "5bf77b8282d0938d59104b5e4e615c30c3b4fbdc089dab2ccc1bbd019da14098",
}
V26_FEASIBILITY_CODE_HASH = "beb4c739c05a225b5fe41e796a6d7a7c0fa60239d6b14dab51f28ba6d83d75ad"
V26_FEASIBILITY_TEST_HASH = "e5aba6f3218c2faf44c8196e80d6d34774a91e0e5a910144c1bf18f24615c743"
V27_FIXED_INPUT_HASHES = {
    "guide/RC_HSG_Paper_Spec_v2_6_2026-08-24.md": "174f0ee08870cc045a75336d3fc7138c97a99e78e5adfb109aed74b5c5144aaa",
    "artifacts/spec_review/rc_hsg_v26_n1_block_feasibility_review.md": "b44e0a97c57d8e51e3e8365c56781c88b37328acc28d21f40f070e876d421e87",
    "artifacts/nulls/n1_block_assignment_v1.jsonl": "d0acc5e5fe78bc36a69cb04b6f605983c675e49a764538ae1665f86a28acee04",
    "artifacts/nulls/n1_block_feasibility.yaml": "90a6178100f507299e12223d15291699aad84e4b58bb52e29843dbf99ee6f771",
    "reports/n1_block_feasibility.md": "5bf77b8282d0938d59104b5e4e615c30c3b4fbdc089dab2ccc1bbd019da14098",
    "scripts/audit_n1_block_feasibility.py": "beb4c739c05a225b5fe41e796a6d7a7c0fa60239d6b14dab51f28ba6d83d75ad",
    "runs/2026-08-24_017_n1_block_feasibility.md": "bf61b04a19f7586d44aec7d6f5b29b38666cce90225964c8f8af250766370eab",
    "artifacts/split_regimeI.json": "e2c065e5b395053cd655670fede8a2b117f6eb9821af884ca31c6fed3842fbab",
    "artifacts/a1_outer_train_admission_v1.jsonl": "b3c1b4e11855ef4c51c5bd0c2c0009f8a24e390c511d97118c48082fc7febfd5",
    "guide/RC_HSG_Paper_Spec_v2_7_2026-08-24.md": "80d613bcb1eb5e3d3948f71f225ffcab5be52c6593fb141fdf410eb0bd753951",
    "artifacts/spec_review/rc_hsg_v27_n1_mechanism_sampler_review.md": "bd245a03d4244f18381b1008ddbd0504cf7ea28f19407cb254747c20150894eb",
}
V27_IMPLEMENTATION_HASHES = {
    "src/rc_hsg/references/__init__.py": "fc18441cc3803ea12e6638abc60e929319fb14f31c6605e5232e5dfdbf4190d9",
    "src/rc_hsg/references/n1_joint_permutation.py": "888c6965c89c007e7edb4d0bcf513a8cdcaf4201dff6b05a3f7bf75bf7a94ca6",
    "scripts/build_n1_sampler_contract.py": "6b65480881bb1e8988bd1c63c2aa50780f9279e3e0378fa25aed691d5cd0706b",
    "tests/test_n1_joint_permutation.py": "c0b65d1263dc8e887c4b90b850b3708c6bd1d68244b5887705b5c290fb5633eb",
    "tests/test_build_n1_sampler_contract.py": "9ade824954aa897d29dfbbe045b3d47bceb0109ff4947b5db51a680996f45e4b",
}
V27_OUTPUT_HASHES = {
    "artifacts/nulls/n1_contract.yaml": "4fee63f743936db06eea41164f85f67228785872d3fca2098e657b1dc0383729",
    "artifacts/nulls/n1_permutation_manifest_v1.jsonl": "b7e68368799be446af60dcec029458e4e769f6605c1c56c032b76fb069f38c06",
    "reports/n1_selfcheck.md": "53fdb1a08a8f9cc7363a03ddf600ed221eaee85b94744c4ca000e1099cf2943e",
}
V28_FIXED_INPUT_HASHES = {
    "guide/RC_HSG_Paper_Spec_v2_7_2026-08-24.md": "80d613bcb1eb5e3d3948f71f225ffcab5be52c6593fb141fdf410eb0bd753951",
    "artifacts/spec_review/rc_hsg_v27_n1_mechanism_sampler_review.md": "bd245a03d4244f18381b1008ddbd0504cf7ea28f19407cb254747c20150894eb",
    "runs/2026-08-24_018_n1_mechanism_sampler.md": "0b3f9ee0662f3429b3ac6fe0b78148e5b61aa2de21d59bec97f8cc634b90d4e7",
    "src/rc_hsg/references/n1_joint_permutation.py": "888c6965c89c007e7edb4d0bcf513a8cdcaf4201dff6b05a3f7bf75bf7a94ca6",
    "artifacts/nulls/n1_contract.yaml": "4fee63f743936db06eea41164f85f67228785872d3fca2098e657b1dc0383729",
    "artifacts/nulls/n1_permutation_manifest_v1.jsonl": "b7e68368799be446af60dcec029458e4e769f6605c1c56c032b76fb069f38c06",
    "artifacts/a_interface_eligibility_v1.jsonl": "8eded8fb2786747e96b8388d4d91315e39db9f8a9eb25ea69056d219e1e8e1ad",
    "requirements-trust-align.lock.txt": "72a2a3274ef9516dba95a4f4022cacfba0e02d10445e1618da2a569f59381910",
    "guide/RC_HSG_Paper_Spec_v2_8_2026-08-24.md": "f718fc37875a6dac7c539260de054d9f9c52966905b1912cf193d573a0424f23",
    "artifacts/spec_review/rc_hsg_v28_n2_common_phase_sampler_review.md": "66edb1aca13e01f87d1a162b86254bbad87ce207ae208474f46a326e53948ea7",
}
V28_IMPLEMENTATION_HASHES = {
    "src/rc_hsg/references/__init__.py": "9e53c4a8acbe2e965eff422a17f29cb5fa0471a9113914da76c13a498882fc6d",
    "src/rc_hsg/references/n2_common_phase.py": "65fc0c3215a2b289c498e989795db74002642388ca64caa2fea93d7780a5aa7e",
    "scripts/build_n2_sampler_contract.py": "baebfa04bf2381075786d9375e78a741ded32f157ea21da37885bc4001530252",
    "tests/test_n2_common_phase.py": "27b2d1e53123f3af1cd4b78a6fc77ae940afa3978baafa57bf8e99a3a7d157fe",
    "tests/test_build_n2_sampler_contract.py": "3e052367fa95bfd6f3a5a9b5d720c9132dd7f7c55a6b57e9149cfa1c955f376e",
    "tests/test_n1_joint_permutation.py": "e77782c2fa2d302ac9a1aa31246115b0636e81f16c4e0631bffa2bd2d4028437",
}
V28_OUTPUT_HASHES = {
    "artifacts/governance/run018_provenance_correction.yaml": "1ec0274f6604df1fb2691ff67d4a4f03e1a60fc508a87796e01b5d81d5415e01",
    "artifacts/nulls/n2_contract.yaml": "c2713dc4fbe989c1680e02e88c336541482bfcb9e828170b3a225d2466d1377d",
    "reports/n2_selfcheck.md": "042fc06f0627d4b29ead30075bb003800b0305ceb7d67387bc3f3e9d2f15f13c",
}
V293_FIXED_HASHES = {
    "guide/RC_HSG_Paper_Spec_v2_9_2026-08-24.md": "0c9498b440ddc883a490a3d5d8fa1f39d3fc49d9e1d593d07ea63d24b23fc1fd",
    "artifacts/spec_review/rc_hsg_v29_gate_r0_review.md": "31b8d6cfe8f8d0ea96f3c201217710f48fe83a4d4651376aef762a20d5cfdf51",
    "guide/RC_HSG_Paper_Spec_v2_9_1_GATE_R0_PANEL_ADDENDUM_2026-08-24.md": "f33911ec40030f212969b63b90218d6fcb1dc30e7edc83148d67df28fee3c603",
    "artifacts/spec_review/rc_hsg_v291_gate_r0_panel_conflict_resolution.md": "50393d3b4b7c8cd59ce674072f1bdfd3b506847284fe200f22214567ee2f8a93",
    "guide/RC_HSG_Paper_Spec_v2_9_1_2026-08-24.md": "d37692f7ed64c33d53534b5ccdfefa600775c4e66874523a00254242d3205f40",
    "guide/RC_HSG_Paper_Spec_v2_9_2_MODEL_WARNING_ADDENDUM_2026-08-24.md": "49481783458da3a4d0020a914eed54559fb7e1006f8a4132014f9b5a166eff0c",
    "artifacts/spec_review/rc_hsg_v292_model_warning_conflict_resolution.md": "d60980875ad80652f8e55a6ea1935b737286f88089d4324af3b0b51c6e189b5a",
    "guide/RC_HSG_Paper_Spec_v2_9_2_2026-08-24.md": "4a5138bcfe8199d7ab5c9cd90d6a2669c987b624953c63a419df41730858225c",
    "guide/RC_HSG_Paper_Spec_v2_9_3_FIT_CLASS_DOMAIN_ADDENDUM_2026-08-24.md": "48e5d7f5eeb2b705f125bc9e954c6ab644533a19f560de45cd9101c2f3113846",
    "artifacts/spec_review/rc_hsg_v293_fit_class_domain_conflict_resolution.md": "70b331a9ad125404dad74609cdab132a76f5e29ba01a14038c0546346c174c12",
    "guide/RC_HSG_Paper_Spec_v2_9_3_2026-08-24.md": "8650a71144af074ecf6b0ca1e3c92dcc76a9283891c991de0672edfd124f3745",
    "scripts/audit_gate_r0.py": "aae1609e83ec3389ba4b55032804289ff7324024070ce37ac49377e008955d70",
    "tests/test_audit_gate_r0.py": "b67f3ab1e271300c07bd7cfe627b0de2b6fc2aba632c125f9fbc4a03ec231878",
    "artifacts/governance/run019_postcommit_correction.yaml": "6b4bae7b74ba7110d0d933c828c87f3581a46efca44d509d83699c540417d72e",
    "artifacts/gates/gate_r0_logistic_api_equivalence_v1.yaml": "0f9d4232922588a8a9859ad64b6e122362e79f1ae6c0123cf1ce8b0d40b5af34",
    "artifacts/gates/gate_r0_matched_support_v1.jsonl": "3f2eb411e54c730453d1dd8a39c5bfeff0aa34ee278c545ac66d2f24b2af2246",
    "artifacts/gates/gate_r0_panel_v1.jsonl": "2cffa7699e7a29eee4996172a20707678ba1ec3529d35e32b2ca453ad79aa806",
    "artifacts/gates/gate_r0_n2_coverage_v1.jsonl": "820cb97c3db810c927c74ad4792693154746f9d33ae1266bba712a5059b413be",
    "artifacts/gates/gate_r0.yaml": "b1cdf2e4932ea40e833f7835944f604024c5cf28b94ddc1bc97fc005d6dc04a3",
    "reports/gate_r0.md": "b23d07e059ac92630714abdd9a75faedcbf50eac6c34ff6b72250419d1ba4293",
}
FROZEN_RUN_011_HASHES = {
    "artifacts/split_regimeI.json": "e2c065e5b395053cd655670fede8a2b117f6eb9821af884ca31c6fed3842fbab",
    "artifacts/split_regimeII.json": "9643dd5abe953e863e7535989f2f65d0f013a1c775c167e49f7d107545016393",
    "artifacts/split_manifest.yaml": "56ccf23881c4e5dee2f3f00704a8af4847636d116783a9da8c2526fdb5c2549f",
    "artifacts/gate_a_population.yaml": "279e3edf1c41971b6967f74657ec531533977d90ea4dc3d48a5efd63dd295d60",
    "reports/joint_split_population.md": "13755eac6198352b9c4dd6605f95a31b6e859db395bb5e6539a715427f742d09",
}
SNAPSHOT_PATHS = (
    "artifacts/governance/repository_inventory.yaml",
    "artifacts/governance/environment_snapshot.yaml",
    "artifacts/governance/spec_implementation_matrix.yaml",
)
SPEC_VERSION_RE = re.compile(r"^v[0-9]+\.[0-9]+(?:\.[0-9]+)?$")
ACTIVE_SPEC_DECL_RE = re.compile(
    r"Active SPEC:\s*`?([^`\s]+)`?\s*\(version\s*`?(v[0-9]+\.[0-9]+(?:\.[0-9]+)?)`?\)",
    re.IGNORECASE,
)
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
FOREIGN_PROJECT_MARKERS = {
    "EQ-ANMA",
    "CSPE",
    "711340d",
    "STRUCTURAL_NO_GO_N50",
}


def _error(errors: list[str], code: str, detail: str) -> None:
    errors.append(f"{code}: {detail}")


def _load_yaml(path: Path, errors: list[str], label: str) -> Any:
    try:
        with path.open("r", encoding="utf-8") as handle:
            value = yaml.safe_load(handle)
    except FileNotFoundError:
        _error(errors, "FILE_MISSING", f"{label} not found: {path}")
        return None
    except yaml.YAMLError as exc:
        _error(errors, "YAML_INVALID", f"{label}: {exc}")
        return None
    if value is None:
        _error(errors, "YAML_EMPTY", label)
    return value


def _safe_relative_path(root: Path, value: Any) -> Path | None:
    if not isinstance(value, str) or not value.strip():
        return None
    candidate = Path(value)
    if candidate.is_absolute() or ".." in candidate.parts:
        return None
    resolved = (root / candidate).resolve()
    try:
        resolved.relative_to(root.resolve())
    except ValueError:
        return None
    return resolved


def _check_active_spec_entrypoints(root: Path, project: dict[str, Any], errors: list[str]) -> None:
    """Fail closed when any live recovery entry point names another SPEC."""
    expected_path = project.get("spec_path")
    expected_version = project.get("spec_version")
    for relative in ("AGENTS.md", "AI_START_HERE.md", "HANDOFF.md", "PACKAGE_README.md"):
        path = root / relative
        try:
            content = path.read_text(encoding="utf-8")
        except FileNotFoundError:
            _error(errors, "FILE_MISSING", f"active SPEC entry point not found: {path}")
            continue
        except OSError as exc:
            _error(errors, "FILE_UNREADABLE", f"{relative}: {type(exc).__name__}")
            continue
        declaration = ACTIVE_SPEC_DECL_RE.search(content)
        if declaration is None:
            _error(errors, "ENTRYPOINT_SPEC_MISMATCH", f"{relative}: Active SPEC declaration missing")
            continue
        declared_path, declared_version = declaration.groups()
        if declared_path != expected_path:
            _error(errors, "ENTRYPOINT_SPEC_MISMATCH", f"{relative}: path {declared_path!r} != {expected_path!r}")
        if declared_version != expected_version:
            _error(errors, "ENTRYPOINT_SPEC_MISMATCH", f"{relative}: version {declared_version!r} != {expected_version!r}")


def _prerequisites_done(task: dict[str, Any], tasks: dict[str, Any]) -> bool:
    prerequisites = task.get("prerequisites")
    if not isinstance(prerequisites, list):
        return False
    return all(
        isinstance(tasks.get(task_id), dict)
        and tasks[task_id].get("status") == "DONE"
        for task_id in prerequisites
    )


def active_blocked_task_ids(state: dict[str, Any]) -> set[str]:
    blocked: set[str] = set()
    blockers = state.get("blockers", [])
    if not isinstance(blockers, list):
        return blocked
    for blocker in blockers:
        if not isinstance(blocker, dict):
            continue
        blocks = blocker.get("blocks", [])
        if isinstance(blocks, list):
            blocked.update(item for item in blocks if isinstance(item, str))
    return blocked


def ready_tasks(tasks: dict[str, Any], state: dict[str, Any]) -> list[str]:
    """Return valid READY tasks in the mandated deterministic order."""

    blocked = active_blocked_task_ids(state)
    candidates = [
        task_id
        for task_id, task in tasks.items()
        if isinstance(task, dict)
        and task.get("status") == "READY"
        and task_id not in blocked
        and _prerequisites_done(task, tasks)
    ]

    def rank(task_id: str) -> tuple[int, int, str]:
        task = tasks[task_id]
        priority = task.get("priority", 1_000_000)
        try:
            numeric_priority = int(priority)
        except (TypeError, ValueError):
            numeric_priority = 1_000_000
        return (
            0 if task.get("critical_path") is True else 1,
            numeric_priority,
            task_id,
        )

    return sorted(candidates, key=rank)


def _check_cycles(tasks: dict[str, Any], errors: list[str]) -> None:
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(task_id: str, trail: list[str]) -> None:
        if task_id in visiting:
            _error(
                errors,
                "DEPENDENCY_CYCLE",
                " -> ".join(trail + [task_id]),
            )
            return
        if task_id in visited:
            return
        visiting.add(task_id)
        task = tasks.get(task_id)
        if isinstance(task, dict):
            prerequisites = task.get("prerequisites", [])
            if isinstance(prerequisites, list):
                for prerequisite in prerequisites:
                    if prerequisite in tasks:
                        visit(prerequisite, trail + [task_id])
        visiting.remove(task_id)
        visited.add(task_id)

    for task_id in tasks:
        visit(task_id, [])


def _run_record_path(root: Path, completed_by_run: Any) -> Path | None:
    if not isinstance(completed_by_run, str) or not completed_by_run.strip():
        return None
    value = completed_by_run.strip()
    relative = value if value.startswith("runs/") else f"runs/{value}.md"
    return _safe_relative_path(root, relative)


def _require_done(
    tasks: dict[str, Any], required: Iterable[str], errors: list[str], code: str
) -> None:
    missing = [
        task_id
        for task_id in required
        if not isinstance(tasks.get(task_id), dict)
        or tasks[task_id].get("status") != "DONE"
    ]
    if missing:
        _error(errors, code, "required DONE tasks: " + ", ".join(missing))


def _check_gate_order(tasks: dict[str, Any], errors: list[str]) -> None:
    if tasks.get("GATE_R0", {}).get("status") == "DONE":
        _require_done(
            tasks,
            ("S0_LEAKAGE_AUDIT", "S0_A1_ADMISSION", "S0_N1_SAMPLER", "S0_N2_SAMPLER"),
            errors,
            "GATE_R0_ORDER",
        )

    if tasks.get("ROUTE_LOCK", {}).get("status") == "DONE":
        _require_done(
            tasks,
            (
                "S0_ABSOLUTE_HSG",
                "S0_RC_HSG_CORE",
                "S0_FLAT_RC",
                "S0_PMI_BASELINE",
                "S0_CALIBRATION_CONTRACT",
                "S0_LEAKAGE_AUDIT",
                "S0_ALIGN_UNIT_COST",
            ),
            errors,
            "ROUTE_LOCK_ORDER",
        )

    if tasks.get("GATE_R", {}).get("status") == "DONE":
        _require_done(
            tasks,
            ("ROUTE_LOCK", "S0_ABSOLUTE_HSG", "S0_RC_HSG_CORE"),
            errors,
            "GATE_R_ORDER",
        )

    if tasks.get("GATE_C", {}).get("status") == "DONE":
        _require_done(
            tasks,
            ("ROUTE_LOCK", "S0_RC_HSG_CORE", "S0_CALIBRATION_CONTRACT"),
            errors,
            "GATE_C_ORDER",
        )

    if tasks.get("GATE_H", {}).get("status") == "DONE":
        _require_done(
            tasks,
            ("ROUTE_LOCK", "S0_RC_HSG_CORE", "S0_FLAT_RC"),
            errors,
            "GATE_H_ORDER",
        )

    if tasks.get("MECHANISM_A", {}).get("status") == "DONE":
        _require_done(
            tasks,
            ("ROUTE_LOCK", "GATE_R0", "S0_REFERENCE_FEATURES", "S0_GATE_A_POPULATION_E5"),
            errors,
            "MECHANISM_A_ORDER",
        )

    if tasks.get("MAIN_EXPERIMENT", {}).get("status") == "DONE":
        _require_done(
            tasks,
            (
                "ROUTE_LOCK",
                "GATE_R",
                "GATE_C",
                "GATE_H",
                "MECHANISM_A",
                "S0_LEAKAGE_AUDIT",
                "S0_ALIGN_UNIT_COST",
            ),
            errors,
            "MAIN_EXPERIMENT_ORDER",
        )


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _check_v21_contract(root: Path, state: dict[str, Any], tasks: dict[str, Any], errors: list[str]) -> None:
    project = state.get("project", {})
    if project.get("spec_version") != "v2.1":
        return

    if len(tasks) != 67:
        _error(errors, "V21_TASK_COUNT_MISMATCH", f"expected 67, got {len(tasks)}")
    done = sum(isinstance(task, dict) and task.get("status") == "DONE" for task in tasks.values())
    if done != 29:
        _error(errors, "V21_DONE_COUNT_MISMATCH", f"expected 29, got {done}")
    ready = [task_id for task_id, task in tasks.items() if isinstance(task, dict) and task.get("status") == "READY"]
    if ready != ["S0_A_INTERFACE"]:
        _error(errors, "V21_READY_SET_MISMATCH", repr(ready))
    if tasks.get("S0_A_INTERFACE", {}).get("owner") != "CODEX":
        _error(errors, "V21_A_INTERFACE_OWNER_MISMATCH", repr(tasks.get("S0_A_INTERFACE", {}).get("owner")))

    for task_id in V21_SUPERSEDED_TASKS:
        task = tasks.get(task_id, {})
        if task.get("status") != "SKIPPED" or task.get("critical_path") is not False or task.get("skip_reason") != "SUPERSEDED_BY_RC_HSG_V21":
            _error(errors, "V21_SUPERSEDED_TASK_MISMATCH", task_id)

    for task_id, expected in V21_DEPENDENCIES.items():
        actual = tasks.get(task_id, {}).get("prerequisites")
        if not isinstance(actual, list) or set(actual) != expected or len(actual) != len(expected):
            _error(errors, "V21_DEPENDENCY_MISMATCH", f"{task_id}: {actual!r}")

    gates = state.get("gates")
    if not isinstance(gates, dict) or set(gates) != set(V21_ACTIVE_GATES):
        _error(errors, "V21_ACTIVE_GATE_SET_MISMATCH", repr(sorted(gates) if isinstance(gates, dict) else gates))

    policy = _load_yaml(root / "artifacts/backbone_a_policy.yaml", errors, "backbone A policy")
    if isinstance(policy, dict):
        expected_selected = {
            "implementation": "PROJECT_NATIVE_CLEAN_ROOM",
            "external_source_code_copied": False,
            "pretrained_checkpoint": None,
            "weight_download_required": False,
            "input_channels": 105,
            "sampling_hz": 500,
            "input_unit": "RELEASE_NATIVE_AMPLITUDE_UNRESOLVED",
            "physical_unit_conversion": "NONE",
            "channel_interpolation": False,
            "processed_reference": "common-average",
            "per_trial_transform": {
                "center": "channel_median",
                "scale": "max(1.4826_times_MAD,centered_RMS,1e-6)",
                "clip": [-20.0, 20.0],
            },
            "window_samples": 500,
            "hop_samples": 250,
            "window_function": "HANN",
            "bands_hz": [[1, 4], [4, 8], [8, 10], [10, 13], [13, 20], [20, 30], [30, 45], [55, 75]],
            "feature": "LOG_RELATIVE_BANDPOWER",
            "feature_epsilon": 1.0e-12,
            "token_input_dim": 840,
            "projection_dim": 256,
            "temporal_encoder_layers": 2,
            "attention_heads": 4,
            "feedforward_dim": 512,
            "dropout": 0.10,
            "position": "SINUSOIDAL",
            "output_contract": {"window_embeddings": "L_BY_256", "mask": "L", "pooled_embedding": 256},
            "initialization": "DETERMINISTIC_PROJECT_OWNED_RANDOM_INIT_PER_FROZEN_MAIN_SEED",
            "trainability": "TRAIN_FROM_SCRATCH_ALL_METHODS_SHARED",
            "peft": False,
            "test_fitted_scaling": False,
        }
        if policy.get("schema_version") != 1 or policy.get("artifact") != "RC_HSG_BACKBONE_A_POLICY_V1" or policy.get("policy_id") != "RC_HSG_NATIVE_SPECTRAL_A1_V1" or policy.get("decision_basis") != "OUTCOME_BLIND_AUTHOR_POLICY":
            _error(errors, "V21_A_POLICY_IDENTITY_MISMATCH", "schema/artifact/policy/decision basis")
        if policy.get("selected") != expected_selected:
            _error(errors, "V21_A_POLICY_SELECTED_MISMATCH", "selected interface differs from frozen policy")
        expected_rejections = {
            "TRUST_ALIGN_A1_SPECTRAL": "REJECT_PRIMARY_EXTERNAL_SOURCE_LICENSE_NOT_FOUND_NO_CODE_COPY",
            "TRUST_ALIGN_LABRAM_A3": "REJECT_PRIMARY_UNIT_CHANNEL_FILTER_CHECKPOINT_INTERFACE_UNRESOLVED",
            "OFFICIAL_NEUROLM_B_VQ": "REJECT_PRIMARY_MICROVOLT_CHANNEL_ADAPTER_AND_UNDOWNLOADED_WEIGHT_GAPS",
        }
        ledger = policy.get("candidate_ledger", {})
        actual_rejections = {key: value.get("primary_decision") for key, value in ledger.items()} if isinstance(ledger, dict) else {}
        if actual_rejections != expected_rejections:
            _error(errors, "V21_A_POLICY_REJECTION_MISMATCH", repr(actual_rejections))

    for relative, expected in FROZEN_RUN_011_HASHES.items():
        path = root / relative
        if not path.is_file():
            _error(errors, "V21_FROZEN_ARTIFACT_MISSING", relative)
        elif _sha256(path) != expected:
            _error(errors, "V21_FROZEN_ARTIFACT_HASH_MISMATCH", relative)

    split = _load_yaml(root / "artifacts/split_manifest.yaml", errors, "split manifest")
    if isinstance(split, dict) and split.get("assertions", {}).get("test_status") != "LOCKED_UNTIL_ROUTE_LOCK":
        _error(errors, "V21_TEST_LOCK_MISMATCH", repr(split.get("assertions", {}).get("test_status")))


def _check_v22_contract(root: Path, state: dict[str, Any], tasks: dict[str, Any], errors: list[str]) -> None:
    if state.get("project", {}).get("spec_version") != "v2.2":
        return

    status_counts = {
        status: sum(isinstance(task, dict) and task.get("status") == status for task in tasks.values())
        for status in ("DONE", "SKIPPED", "BLOCKED", "READY")
    }
    if len(tasks) != 68 or status_counts != {"DONE": 31, "SKIPPED": 8, "BLOCKED": 28, "READY": 1}:
        _error(errors, "V22_TASK_STATE_MISMATCH", f"tasks={len(tasks)} statuses={status_counts!r}")
    ready = [task_id for task_id, task in tasks.items() if isinstance(task, dict) and task.get("status") == "READY"]
    if ready != ["S0_A1_FRONTEND"] or tasks.get("S0_A1_FRONTEND", {}).get("owner") != "CODEX":
        _error(errors, "V22_READY_SET_MISMATCH", repr(ready))
    if tasks.get("SPEC_V22_REVIEW", {}).get("status") != "DONE" or tasks.get("S0_A_INTERFACE", {}).get("status") != "DONE":
        _error(errors, "V22_COMPLETED_CHAIN_MISMATCH", "SPEC_V22_REVIEW or S0_A_INTERFACE")
    for task_id, expected in V22_DEPENDENCIES.items():
        actual = tasks.get(task_id, {}).get("prerequisites")
        if not isinstance(actual, list) or set(actual) != expected or len(actual) != len(expected):
            _error(errors, "V22_DEPENDENCY_MISMATCH", f"{task_id}: {actual!r}")
    for task_id in V21_SUPERSEDED_TASKS:
        task = tasks.get(task_id, {})
        if task.get("status") != "SKIPPED" or task.get("critical_path") is not False or task.get("skip_reason") != "SUPERSEDED_BY_RC_HSG_V21":
            _error(errors, "V22_SUPERSEDED_TASK_MISMATCH", task_id)

    blockers = {item.get("id"): item for item in state.get("blockers", []) if isinstance(item, dict)}
    b8 = blockers.get("B_V8_A_REAL_FRONTEND_UNVALIDATED")
    if "B_V7_A_INTERFACE_UNIMPLEMENTED" in blockers or not isinstance(b8, dict) or set(b8.get("blocks", [])) != V22_B8_BLOCKS:
        _error(errors, "V22_B8_BLOCKER_MISMATCH", repr(b8))
    superseded = {item.get("id"): item for item in state.get("superseded_blockers", []) if isinstance(item, dict)}
    if superseded.get("B_V7_A_INTERFACE_UNIMPLEMENTED", {}).get("closed_by") != "S0_A_INTERFACE":
        _error(errors, "V22_B7_CLOSURE_MISMATCH", repr(superseded.get("B_V7_A_INTERFACE_UNIMPLEMENTED")))

    for relative, expected in {**FROZEN_RUN_011_HASHES, **V22_OUTPUT_HASHES}.items():
        path = root / relative
        if not path.is_file() or _sha256(path) != expected:
            _error(errors, "V22_ARTIFACT_HASH_MISMATCH", relative)
    policy_path = root / "artifacts/backbone_a_policy.yaml"
    if not policy_path.is_file() or _sha256(policy_path) != "034a523119f12f648266d94e0499179882fbe181584d10c1af17a3502a797425":
        _error(errors, "V22_A_POLICY_HASH_MISMATCH", "artifacts/backbone_a_policy.yaml")
    implementation_path = root / "src/rc_hsg/backbones/native_spectral_a1.py"
    if not implementation_path.is_file() or _sha256(implementation_path) != "71ae12d65cc0acc6fd5870434e141ee7d849eb8befa718a84fb99cb86ed533d9":
        _error(errors, "V22_IMPLEMENTATION_HASH_MISMATCH", "src/rc_hsg/backbones/native_spectral_a1.py")

    contract = _load_yaml(root / "artifacts/backbone_a_contract.yaml", errors, "backbone A contract")
    expected_keys = [
        "schema_version", "artifact", "policy_id", "spec_version", "baseline_commit",
        "input_artifacts", "input_contract", "preprocessing_contract", "spectral_contract",
        "encoder_contract", "output_contract", "initialization_contract", "eligibility_contract",
        "acceptance_counts", "implementation", "prohibited_features", "prohibited_actions", "evidence_scope",
    ]
    if isinstance(contract, dict):
        implementation = contract.get("implementation", {})
        if (
            list(contract) != expected_keys
            or contract.get("schema_version") != 1
            or contract.get("artifact") != "RC_HSG_NATIVE_SPECTRAL_A1_CONTRACT_V1"
            or contract.get("policy_id") != "RC_HSG_NATIVE_SPECTRAL_A1_V1"
            or contract.get("spec_version") != "v2.2"
            or contract.get("baseline_commit") != "91997faa1de1616d1eb662cd36edc1547613206d"
            or contract.get("evidence_scope") != "SYNTHETIC_INTERFACE_AND_COMMITTED_METADATA_ONLY_NO_REAL_EEG_VALUES_NO_OUTCOMES"
            or implementation.get("trainable_parameter_count") != 1_270_528
            or implementation.get("real_eeg_validated") is not False
            or implementation.get("code_sha256") != "71ae12d65cc0acc6fd5870434e141ee7d849eb8befa718a84fb99cb86ed533d9"
        ):
            _error(errors, "V22_A_CONTRACT_MISMATCH", "header, order, implementation, or evidence scope")
        expected_counts = {
            "train_fit": {"total_rows": 2832, "eligible": 2797, "forced_l0": 35, "full_windows": 29263},
            "inner_val": {"total_rows": 709, "eligible": 700, "forced_l0": 9, "full_windows": 6482},
            "cal": {"total_rows": 1171, "eligible": 1156, "forced_l0": 15, "full_windows": 11558},
            "test": {"total_rows": 1193, "eligible": 1179, "forced_l0": 14, "full_windows": 13219},
            "total": {"total_rows": 5905, "eligible": 5832, "forced_l0": 73, "full_windows": 60522},
        }
        if contract.get("acceptance_counts", {}).get("by_role") != expected_counts:
            _error(errors, "V22_ACCEPTANCE_COUNT_MISMATCH", "contract by_role")

    eligibility_path = root / "artifacts/a_interface_eligibility_v1.jsonl"
    rows: list[dict[str, Any]] = []
    try:
        with eligibility_path.open("r", encoding="utf-8") as handle:
            rows = [json.loads(line) for line in handle]
    except (OSError, json.JSONDecodeError) as exc:
        _error(errors, "V22_ELIGIBILITY_PARSE_ERROR", type(exc).__name__)
    expected_fields = [
        "occurrence_id", "subject", "slot", "role", "calibration_reserve",
        "raw_samples", "window_count", "a_interface_status", "action",
    ]
    short = [row for row in rows if row.get("a_interface_status") == "A_INTERFACE_SHORT_SEGMENT"]
    if (
        len(rows) != 5905
        or any(list(row) != expected_fields for row in rows)
        or rows != sorted(rows, key=lambda row: (row.get("subject"), row.get("slot"), row.get("occurrence_id")))
        or len(short) != 73
        or any(row.get("window_count") != 0 or row.get("action") != "FORCED_L0_NO_FRONTEND" for row in short)
        or sum(row.get("window_count", 0) for row in rows) != 60522
    ):
        _error(errors, "V22_ELIGIBILITY_MISMATCH", f"rows={len(rows)} short={len(short)}")
    split = _load_yaml(root / "artifacts/split_manifest.yaml", errors, "split manifest")
    if isinstance(split, dict) and split.get("assertions", {}).get("test_status") != "LOCKED_UNTIL_ROUTE_LOCK":
        _error(errors, "V22_TEST_LOCK_MISMATCH", repr(split.get("assertions", {}).get("test_status")))


def _check_v23_contract(root: Path, state: dict[str, Any], tasks: dict[str, Any], errors: list[str]) -> None:
    if state.get("project", {}).get("spec_version") != "v2.3":
        return

    status_counts = {
        status: sum(isinstance(task, dict) and task.get("status") == status for task in tasks.values())
        for status in ("DONE", "SKIPPED", "BLOCKED", "READY")
    }
    expected_statuses = {"DONE": 33, "SKIPPED": 8, "BLOCKED": 28, "READY": 1}
    if len(tasks) != 70 or status_counts != expected_statuses:
        _error(errors, "V23_TASK_STATE_MISMATCH", f"tasks={len(tasks)} statuses={status_counts!r}")
    ready = [task_id for task_id, task in tasks.items() if isinstance(task, dict) and task.get("status") == "READY"]
    if ready != ["S0_LEAKAGE_AUDIT"] or tasks.get("S0_LEAKAGE_AUDIT", {}).get("owner") != "CODEX":
        _error(errors, "V23_READY_SET_MISMATCH", repr(ready))
    if tasks.get("SPEC_V23_REVIEW", {}).get("status") != "DONE" or tasks.get("S0_A1_FRONTEND", {}).get("status") != "DONE":
        _error(errors, "V23_COMPLETED_CHAIN_MISMATCH", "SPEC_V23_REVIEW or S0_A1_FRONTEND")
    for task_id, expected in V23_DEPENDENCIES.items():
        actual = tasks.get(task_id, {}).get("prerequisites")
        if not isinstance(actual, list) or set(actual) != expected or len(actual) != len(expected):
            _error(errors, "V23_DEPENDENCY_MISMATCH", f"{task_id}: {actual!r}")

    early = tasks.get("S0_LEAKAGE_AUDIT", {})
    method = tasks.get("S0_METHOD_LEAKAGE_AUDIT", {})
    if early.get("produces") != ["artifacts/a_path_leakage_assertions.yaml", "reports/a_path_leakage_audit.md"]:
        _error(errors, "V23_EARLY_LEAKAGE_TASK_MISMATCH", repr(early.get("produces")))
    if method.get("produces") != ["artifacts/method_leakage_assertions.yaml", "reports/method_leakage_audit.md"]:
        _error(errors, "V23_METHOD_LEAKAGE_TASK_MISMATCH", repr(method.get("produces")))

    blockers = {item.get("id"): item for item in state.get("blockers", []) if isinstance(item, dict)}
    b9 = blockers.get("B_V9_A_FULL_OUTER_TRAIN_ADMISSION_PENDING")
    if "B_V8_A_REAL_FRONTEND_UNVALIDATED" in blockers or not isinstance(b9, dict) or set(b9.get("blocks", [])) != V23_B9_BLOCKS:
        _error(errors, "V23_B9_BLOCKER_MISMATCH", repr(b9))
    if "S0_A1_ADMISSION" in (b9 or {}).get("blocks", []):
        _error(errors, "V23_B9_RESOLVER_BLOCKED", "S0_A1_ADMISSION")
    superseded = {item.get("id"): item for item in state.get("superseded_blockers", []) if isinstance(item, dict)}
    if superseded.get("B_V8_A_REAL_FRONTEND_UNVALIDATED", {}).get("closed_by") != "S0_A1_FRONTEND":
        _error(errors, "V23_B8_CLOSURE_MISMATCH", repr(superseded.get("B_V8_A_REAL_FRONTEND_UNVALIDATED")))

    for relative, expected in {**FROZEN_RUN_011_HASHES, **V22_OUTPUT_HASHES, **V23_OUTPUT_HASHES}.items():
        path = root / relative
        if not path.is_file() or _sha256(path) != expected:
            _error(errors, "V23_ARTIFACT_HASH_MISMATCH", relative)
    policy_path = root / "artifacts/backbone_a_policy.yaml"
    if not policy_path.is_file() or _sha256(policy_path) != "034a523119f12f648266d94e0499179882fbe181584d10c1af17a3502a797425":
        _error(errors, "V23_A_POLICY_HASH_MISMATCH", "artifacts/backbone_a_policy.yaml")
    implementation_path = root / "src/rc_hsg/backbones/native_spectral_a1.py"
    if not implementation_path.is_file() or _sha256(implementation_path) != "71ae12d65cc0acc6fd5870434e141ee7d849eb8befa718a84fb99cb86ed533d9":
        _error(errors, "V23_A_IMPLEMENTATION_HASH_MISMATCH", "src/rc_hsg/backbones/native_spectral_a1.py")

    panel_path = root / "artifacts/a1_frontend_audit_panel_v1.jsonl"
    try:
        with panel_path.open("r", encoding="utf-8") as handle:
            panel = [json.loads(line) for line in handle]
    except (OSError, json.JSONDecodeError) as exc:
        panel = []
        _error(errors, "V23_PANEL_PARSE_ERROR", type(exc).__name__)
    fields = [
        "subject", "slot", "occurrence_id", "role", "raw_samples", "window_count",
        "selection_reason", "a_interface_status", "action", "source_file",
        "source_field", "source_dataset_read",
    ]
    real = [row for row in panel if row.get("source_dataset_read") is True]
    short = [row for row in panel if row.get("source_dataset_read") is False]
    if (
        len(panel) != 151
        or any(list(row) != fields for row in panel)
        or panel != sorted(panel, key=lambda row: (row.get("subject"), row.get("slot"), row.get("occurrence_id")))
        or len(real) != 107
        or len(short) != 44
        or sum(row.get("window_count", 0) for row in real) != 1452
        or len({row.get("subject") for row in real}) != 18
        or any(row.get("source_field") != "rawData" for row in panel)
        or any(row.get("action") != "FORCED_L0_NO_FRONTEND" for row in short)
    ):
        _error(errors, "V23_PANEL_MISMATCH", f"rows={len(panel)} real={len(real)} short={len(short)}")

    freeze = _load_yaml(root / "artifacts/a1_frontend_freeze.yaml", errors, "A1 frontend freeze")
    expected_keys = [
        "schema_version", "artifact", "spec_version", "baseline_commit", "task", "policy_id",
        "evidence_scope", "input_artifacts", "authorized_scope", "panel_contract",
        "source_identity_contract", "loader_contract", "execution_contract", "acceptance_counts",
        "check_results", "implementation", "prohibited", "safety", "downstream_boundary",
    ]
    if isinstance(freeze, dict):
        counts = freeze.get("acceptance_counts", {})
        checks = freeze.get("check_results", {})
        boundary = freeze.get("downstream_boundary", {})
        implementation = freeze.get("implementation", {})
        validator_path = root / "scripts/validate_a1_frontend.py"
        if (
            list(freeze) != expected_keys
            or freeze.get("artifact") != "RC_HSG_A1_REAL_FRONTEND_VALIDATION_V1"
            or freeze.get("spec_version") != "v2.3"
            or freeze.get("baseline_commit") != "237788090dcb20e533f304f63ae8feb2f545fe0b"
            or freeze.get("task") != "S0_A1_FRONTEND"
            or freeze.get("evidence_scope") != "BOUNDED_OUTER_TRAIN_REAL_EEG_FRONTEND_SELF_CHECK_NO_OUTCOMES_NO_TRAINING_NOT_FULL_ADMISSION"
            or counts.get("real_distinct_rows_read") != 107
            or counts.get("panel_windows") != 1452
            or counts.get("short_no_read") != 44
            or checks.get("cpu_status") != "PASS"
            or checks.get("cuda", {}).get("status") != "PASS"
            or checks.get("cuda", {}).get("rows") != 20
            or checks.get("cuda", {}).get("windows") != 199
            or boundary != {"full_outer_train_admission_completed": False, "remaining_eligible_rows_not_read": 3390, "next_task": "S0_LEAKAGE_AUDIT"}
            or not validator_path.is_file()
            or implementation.get("validator_sha256") != _sha256(validator_path)
        ):
            _error(errors, "V23_FRONTEND_FREEZE_MISMATCH", "header, counts, checks, boundary, or validator hash")

    split = _load_yaml(root / "artifacts/split_manifest.yaml", errors, "split manifest")
    if isinstance(split, dict) and split.get("assertions", {}).get("test_status") != "LOCKED_UNTIL_ROUTE_LOCK":
        _error(errors, "V23_TEST_LOCK_MISMATCH", repr(split.get("assertions", {}).get("test_status")))


def _check_v24_contract(root: Path, state: dict[str, Any], tasks: dict[str, Any], errors: list[str]) -> None:
    if state.get("project", {}).get("spec_version") != "v2.4":
        return

    status_counts = {
        status: sum(isinstance(task, dict) and task.get("status") == status for task in tasks.values())
        for status in ("DONE", "SKIPPED", "BLOCKED", "READY")
    }
    expected_statuses = {"DONE": 35, "SKIPPED": 8, "BLOCKED": 27, "READY": 1}
    if len(tasks) != 71 or status_counts != expected_statuses:
        _error(errors, "V24_TASK_STATE_MISMATCH", f"tasks={len(tasks)} statuses={status_counts!r}")
    ready = [task_id for task_id, task in tasks.items() if isinstance(task, dict) and task.get("status") == "READY"]
    if ready != ["S0_A1_ADMISSION"] or tasks.get("S0_A1_ADMISSION", {}).get("owner") != "CODEX":
        _error(errors, "V24_READY_SET_MISMATCH", repr(ready))
    if tasks.get("SPEC_V24_REVIEW", {}).get("status") != "DONE" or tasks.get("S0_LEAKAGE_AUDIT", {}).get("status") != "DONE":
        _error(errors, "V24_COMPLETED_CHAIN_MISMATCH", "SPEC_V24_REVIEW or S0_LEAKAGE_AUDIT")
    for task_id, expected in V23_DEPENDENCIES.items():
        actual = tasks.get(task_id, {}).get("prerequisites")
        if not isinstance(actual, list) or set(actual) != expected or len(actual) != len(expected):
            _error(errors, "V24_DEPENDENCY_MISMATCH", f"{task_id}: {actual!r}")

    project = state.get("project", {})
    if (
        project.get("spec_path") != "guide/RC_HSG_Paper_Spec_v2_4_2026-08-24.md"
        or project.get("baseline_commit") != "dc105709563cf9eb216f1c28f82fdf754e7b0683"
        or project.get("reviewed_commit") != "dc105709563cf9eb216f1c28f82fdf754e7b0683"
        or project.get("repository_status") != "RC_HSG_V24_A_PATH_LEAKAGE_PASSED_FULL_ADMISSION_PENDING"
        or state.get("last_completed_task") != "S0_LEAKAGE_AUDIT"
        or state.get("recommended_next_task") != "S0_A1_ADMISSION"
        or state.get("route", {}).get("locked") is not None
    ):
        _error(errors, "V24_PROJECT_STATE_MISMATCH", repr(project))

    blockers = {item.get("id"): item for item in state.get("blockers", []) if isinstance(item, dict)}
    b9 = blockers.get("B_V9_A_FULL_OUTER_TRAIN_ADMISSION_PENDING")
    if not isinstance(b9, dict) or set(b9.get("blocks", [])) != V23_B9_BLOCKS or "S0_A1_ADMISSION" in b9.get("blocks", []):
        _error(errors, "V24_B9_RESOLVER_MISMATCH", repr(b9))

    for relative, expected in {**FROZEN_RUN_011_HASHES, **V22_OUTPUT_HASHES, **V23_OUTPUT_HASHES, **V24_OUTPUT_HASHES}.items():
        path = root / relative
        if not path.is_file() or _sha256(path) != expected:
            _error(errors, "V24_ARTIFACT_HASH_MISMATCH", relative)
    for relative, expected in {
        "artifacts/backbone_a_policy.yaml": "034a523119f12f648266d94e0499179882fbe181584d10c1af17a3502a797425",
        "src/rc_hsg/backbones/native_spectral_a1.py": "71ae12d65cc0acc6fd5870434e141ee7d849eb8befa718a84fb99cb86ed533d9",
        "scripts/validate_a1_frontend.py": "ecc84a0363629e919409321cdc73327b6e3c7e779e224a18ab55a6b6ac6777cd",
    }.items():
        path = root / relative
        if not path.is_file() or _sha256(path) != expected:
            _error(errors, "V24_ARTIFACT_HASH_MISMATCH", relative)
    audit_code = root / "scripts/audit_a_path_leakage.py"
    if not audit_code.is_file() or _sha256(audit_code) != "797618af0113a2f8f357ea8c91f53de7b9375afcbb3860baf437ebc1bfbe5e24":
        _error(errors, "V24_AUDIT_CODE_HASH_MISMATCH", "scripts/audit_a_path_leakage.py")

    artifact = _load_yaml(root / "artifacts/a_path_leakage_assertions.yaml", errors, "A-path leakage assertions")
    expected_keys = [
        "schema_version", "artifact", "spec_version", "baseline_commit", "task",
        "evidence_scope", "input_artifacts", "audited_components", "frozen_scope",
        "assertions", "mutation_tests", "prohibited", "safety", "downstream_boundary",
    ]
    if isinstance(artifact, dict):
        assertions = artifact.get("assertions", [])
        mutations = artifact.get("mutation_tests", [])
        safety = artifact.get("safety", {})
        boundary = artifact.get("downstream_boundary", {})
        if (
            list(artifact) != expected_keys
            or artifact.get("artifact") != "RC_HSG_A_PATH_LEAKAGE_ASSERTIONS_V1"
            or artifact.get("spec_version") != "v2.4"
            or artifact.get("baseline_commit") != "dc105709563cf9eb216f1c28f82fdf754e7b0683"
            or artifact.get("task") != "S0_LEAKAGE_AUDIT"
            or len(assertions) != 12
            or any(item.get("status") != "PASS" for item in assertions if isinstance(item, dict))
            or len(mutations) != 12
            or any(item.get("status") != "PASS_REJECTED" for item in mutations if isinstance(item, dict))
            or safety != {
                "production_hdf5_opened": False,
                "new_real_eeg_values_read": False,
                "real_frontend_validator_executed": False,
                "text_or_outcome_read": False,
                "training_or_parameter_update": False,
                "test_status": "LOCKED_UNTIL_ROUTE_LOCK",
            }
            or boundary != {
                "full_outer_train_admission_completed": False,
                "remaining_eligible_rows_not_read": 3390,
                "method_leakage_audit_completed": False,
                "full_method_leakage_pass_claimed": False,
                "next_task": "S0_A1_ADMISSION",
            }
        ):
            _error(errors, "V24_AUDIT_ARTIFACT_MISMATCH", "header, assertions, mutations, safety, or boundary")


def _check_v25_contract(root: Path, state: dict[str, Any], tasks: dict[str, Any], errors: list[str]) -> None:
    if state.get("project", {}).get("spec_version") != "v2.5":
        return

    status_counts = {
        status: sum(isinstance(task, dict) and task.get("status") == status for task in tasks.values())
        for status in ("DONE", "SKIPPED", "BLOCKED", "READY")
    }
    expected_statuses = {"DONE": 37, "SKIPPED": 8, "BLOCKED": 26, "READY": 1}
    if len(tasks) != 72 or status_counts != expected_statuses:
        _error(errors, "V25_TASK_STATE_MISMATCH", f"tasks={len(tasks)} statuses={status_counts!r}")
    ready = [task_id for task_id, task in tasks.items() if isinstance(task, dict) and task.get("status") == "READY"]
    if ready != ["S0_N1_BLOCK_FEASIBILITY"] or tasks.get("S0_N1_BLOCK_FEASIBILITY", {}).get("owner") != "CHATGPT_OR_AUTHOR":
        _error(errors, "V25_READY_SET_MISMATCH", repr(ready))
    if tasks.get("SPEC_V25_REVIEW", {}).get("status") != "DONE" or tasks.get("S0_A1_ADMISSION", {}).get("status") != "DONE":
        _error(errors, "V25_COMPLETED_CHAIN_MISMATCH", "SPEC_V25_REVIEW or S0_A1_ADMISSION")
    if tasks.get("SPEC_V25_REVIEW", {}).get("prerequisites") != ["SPEC_V24_REVIEW"]:
        _error(errors, "V25_SPEC_DEPENDENCY_MISMATCH", repr(tasks.get("SPEC_V25_REVIEW", {}).get("prerequisites")))

    project = state.get("project", {})
    if (
        project.get("spec_path") != "guide/RC_HSG_Paper_Spec_v2_5_2026-08-24.md"
        or project.get("baseline_commit") != "07c37b3bb77c3cf396116078b64687dcebb9ee03"
        or project.get("reviewed_commit") != "07c37b3bb77c3cf396116078b64687dcebb9ee03"
        or project.get("repository_status") != "RC_HSG_V25_A1_FULL_OUTER_TRAIN_ADMITTED_N1_FEASIBILITY_PENDING"
        or state.get("last_completed_task") != "S0_A1_ADMISSION"
        or state.get("recommended_next_task") != "S0_N1_BLOCK_FEASIBILITY"
        or state.get("last_run") != "runs/2026-08-24_016_a1_full_outer_train_admission.md"
        or state.get("route", {}).get("locked") is not None
    ):
        _error(errors, "V25_PROJECT_STATE_MISMATCH", repr(project))

    blockers = {item.get("id"): item for item in state.get("blockers", []) if isinstance(item, dict)}
    superseded = {item.get("id"): item for item in state.get("superseded_blockers", []) if isinstance(item, dict)}
    b4 = blockers.get("B_V4_NULL_CONTRACT_UNVERIFIED")
    b9 = superseded.get("B_V9_A_FULL_OUTER_TRAIN_ADMISSION_PENDING")
    if "B_V9_A_FULL_OUTER_TRAIN_ADMISSION_PENDING" in blockers or not isinstance(b9, dict) or b9.get("closed_by") != "S0_A1_ADMISSION":
        _error(errors, "V25_B9_CLOSURE_MISMATCH", repr(b9))
    if not isinstance(b4, dict) or "S0_N1_BLOCK_FEASIBILITY" in b4.get("blocks", []):
        _error(errors, "V25_B4_RESOLVER_MISMATCH", repr(b4))

    immutable_hashes = {
        **FROZEN_RUN_011_HASHES,
        **V22_OUTPUT_HASHES,
        **V23_OUTPUT_HASHES,
        **V24_OUTPUT_HASHES,
        **V25_FIXED_INPUT_HASHES,
        **V25_OUTPUT_HASHES,
    }
    for relative, expected in immutable_hashes.items():
        path = root / relative
        if not path.is_file() or _sha256(path) != expected:
            _error(errors, "V25_ARTIFACT_HASH_MISMATCH", relative)
    admission_code = root / "scripts/admit_a1_outer_train.py"
    if not admission_code.is_file() or _sha256(admission_code) != V25_ADMISSION_CODE_HASH:
        _error(errors, "V25_ADMISSION_CODE_HASH_MISMATCH", "scripts/admit_a1_outer_train.py")

    freeze = _load_yaml(root / "artifacts/a1_outer_train_admission_freeze.yaml", errors, "A1 admission freeze")
    expected_keys = [
        "schema_version", "artifact", "spec_version", "baseline_commit", "task", "policy_id",
        "evidence_scope", "input_artifacts", "population_contract", "reuse_contract",
        "loader_contract", "execution_contract", "acceptance_counts", "check_results",
        "implementation", "prohibited", "safety", "blocker_resolution", "downstream_boundary",
    ]
    if isinstance(freeze, dict):
        counts = freeze.get("acceptance_counts", {})
        execution = freeze.get("execution_contract", {})
        reuse = freeze.get("reuse_contract", {})
        safety = freeze.get("safety", {})
        boundary = freeze.get("downstream_boundary", {})
        implementation = freeze.get("implementation", {})
        checks = freeze.get("check_results", {})
        expected_safety = {
            "production_scan_attempts": 1,
            "run014_panel_arrays_reread": 0,
            "run016_remaining_distinct_arrays_read": 3390,
            "short_arrays_read": 0,
            "calibration_arrays_read": 0,
            "test_arrays_read": 0,
            "text_or_outcome_read": False,
            "training_or_parameter_update": False,
            "representation_or_value_cache_written": False,
            "test_status": "LOCKED_UNTIL_ROUTE_LOCK",
        }
        expected_boundary = {
            "full_outer_train_admission_completed": True,
            "n1_block_feasibility_completed": False,
            "n1_sampler_implemented": False,
            "n2_sampler_implemented": False,
            "method_leakage_audit_completed": False,
            "route_locked": False,
            "next_task": "S0_N1_BLOCK_FEASIBILITY",
        }
        exact_counts = {
            "outer_train_rows": 3541,
            "eligible_cumulative": 3497,
            "short_no_read": 44,
            "full_windows_cumulative": 35745,
            "run014_panel_reused": 107,
            "run014_panel_windows": 1452,
            "run016_remaining_distinct_arrays_read": 3390,
            "run016_windows": 34293,
            "subjects": 18,
            "source_files": 18,
            "minimum_eligible_samples": 513,
            "maximum_eligible_samples": 18436,
            "maximum_windows": 72,
        }
        if (
            list(freeze) != expected_keys
            or freeze.get("schema_version") != 1
            or freeze.get("artifact") != "RC_HSG_A1_FULL_OUTER_TRAIN_ADMISSION_V1"
            or freeze.get("spec_version") != "v2.5"
            or freeze.get("baseline_commit") != "07c37b3bb77c3cf396116078b64687dcebb9ee03"
            or freeze.get("task") != "S0_A1_ADMISSION"
            or freeze.get("policy_id") != "RC_HSG_NATIVE_SPECTRAL_A1_V1"
            or freeze.get("evidence_scope") != "FULL_REGIME_I_OUTER_TRAIN_A1_FRONTEND_ADMISSION_REUSING_RUN014_PANEL_NO_OUTCOMES_NO_TRAINING"
            or any(counts.get(key) != value for key, value in exact_counts.items())
            or counts.get("run016_role_rows") != {"inner_val": 648, "train_fit": 2742}
            or counts.get("run016_role_windows") != {"inner_val": 5882, "train_fit": 28411}
            or counts.get("run016_source_dtype_counts") != {"float64": 3390}
            or reuse.get("eligible_rows") != 107
            or reuse.get("windows") != 1452
            or reuse.get("panel_reread") is not False
            or execution.get("production_scan_attempts") != 1
            or execution.get("scan_order") != ["window_count", "raw_samples", "subject", "slot", "occurrence_id"]
            or execution.get("maximum_batch_rows") != 4
            or execution.get("device_policy_status") != "CUDA_0_SELECTED"
            or safety != expected_safety
            or boundary != expected_boundary
            or implementation.get("admission_sha256") != V25_ADMISSION_CODE_HASH
            or set(checks.values()) != {"PASS"}
        ):
            _error(errors, "V25_ADMISSION_FREEZE_MISMATCH", "header, counts, execution, safety, checks, or boundary")

    ledger_path = root / "artifacts/a1_outer_train_admission_v1.jsonl"
    ledger: list[dict[str, Any]] = []
    try:
        for line_number, line in enumerate(ledger_path.read_text(encoding="utf-8").splitlines(), start=1):
            item = json.loads(line)
            if not isinstance(item, dict):
                raise ValueError(f"line {line_number} is not an object")
            ledger.append(item)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        _error(errors, "V25_ADMISSION_LEDGER_INVALID", str(exc))
        ledger = []
    ledger_fields = [
        "subject", "slot", "occurrence_id", "role", "raw_samples", "window_count",
        "a_interface_status", "action", "evidence_source", "source_file", "source_field",
        "source_dataset_read_run016", "source_dataset_read_cumulative", "source_dtype",
        "source_shape_status", "input_finite_status", "frontend_status", "observed_window_count",
        "window_mask_status", "output_finite_status",
    ]
    if ledger:
        keys = [(item.get("subject"), item.get("slot"), item.get("occurrence_id")) for item in ledger]
        classes = {
            label: sum(item.get("evidence_source") == label for item in ledger)
            for label in ("RUN014_BOUNDED_PANEL_REUSED", "RUN016_STREAMING_FRONTEND_PASS", "SHORT_FORCED_L0_NO_READ")
        }
        run016 = [item for item in ledger if item.get("evidence_source") == "RUN016_STREAMING_FRONTEND_PASS"]
        short = [item for item in ledger if item.get("evidence_source") == "SHORT_FORCED_L0_NO_READ"]
        panel = [item for item in ledger if item.get("evidence_source") == "RUN014_BOUNDED_PANEL_REUSED"]
        if (
            len(ledger) != 3541
            or any(list(item) != ledger_fields for item in ledger)
            or keys != sorted(keys)
            or len(set(keys)) != 3541
            or classes != {"RUN014_BOUNDED_PANEL_REUSED": 107, "RUN016_STREAMING_FRONTEND_PASS": 3390, "SHORT_FORCED_L0_NO_READ": 44}
            or sum(item.get("window_count", -1) for item in ledger) != 35745
            or sum(item.get("window_count", -1) for item in run016) != 34293
            or any(item.get("source_dataset_read_run016") is not True or item.get("source_dataset_read_cumulative") is not True for item in run016)
            or any(item.get("source_dataset_read_run016") is not False or item.get("source_dataset_read_cumulative") is not True or item.get("source_dtype") != "float64" for item in panel)
            or any(item.get("source_dataset_read_run016") is not False or item.get("source_dataset_read_cumulative") is not False or item.get("source_dtype") != "NOT_READ" or item.get("observed_window_count") != 0 for item in short)
            or any(item.get("role") not in {"train_fit", "inner_val"} or item.get("source_field") != "rawData" for item in ledger)
        ):
            _error(errors, "V25_ADMISSION_LEDGER_MISMATCH", "schema, order, classes, counts, reads, roles, or source field")

    split = _load_yaml(root / "artifacts/split_manifest.yaml", errors, "split manifest")
    if isinstance(split, dict) and split.get("assertions", {}).get("test_status") != "LOCKED_UNTIL_ROUTE_LOCK":
        _error(errors, "V25_TEST_LOCK_MISMATCH", repr(split.get("assertions", {}).get("test_status")))


def _check_v26_contract(root: Path, state: dict[str, Any], tasks: dict[str, Any], errors: list[str]) -> None:
    if state.get("project", {}).get("spec_version") != "v2.6":
        return

    status_counts = {
        status: sum(isinstance(task, dict) and task.get("status") == status for task in tasks.values())
        for status in ("DONE", "SKIPPED", "BLOCKED", "READY")
    }
    expected_statuses = {"DONE": 39, "SKIPPED": 8, "BLOCKED": 25, "READY": 1}
    if len(tasks) != 73 or status_counts != expected_statuses:
        _error(errors, "V26_TASK_STATE_MISMATCH", f"tasks={len(tasks)} statuses={status_counts!r}")
    ready = [task_id for task_id, task in tasks.items() if isinstance(task, dict) and task.get("status") == "READY"]
    if ready != ["S0_N1_SAMPLER"] or tasks.get("S0_N1_SAMPLER", {}).get("owner") != "CHATGPT_OR_AUTHOR":
        _error(errors, "V26_READY_SET_MISMATCH", repr(ready))
    if tasks.get("SPEC_V26_REVIEW", {}).get("status") != "DONE" or tasks.get("S0_N1_BLOCK_FEASIBILITY", {}).get("status") != "DONE":
        _error(errors, "V26_COMPLETED_CHAIN_MISMATCH", "SPEC_V26_REVIEW or S0_N1_BLOCK_FEASIBILITY")
    if tasks.get("SPEC_V26_REVIEW", {}).get("prerequisites") != ["SPEC_V25_REVIEW"]:
        _error(errors, "V26_SPEC_DEPENDENCY_MISMATCH", repr(tasks.get("SPEC_V26_REVIEW", {}).get("prerequisites")))

    project = state.get("project", {})
    if (
        project.get("spec_path") != "guide/RC_HSG_Paper_Spec_v2_6_2026-08-24.md"
        or project.get("baseline_commit") != "1c432a02f50cacda99359f630f14cfbfdfb439a1"
        or project.get("reviewed_commit") != "1c432a02f50cacda99359f630f14cfbfdfb439a1"
        or project.get("repository_status") != "RC_HSG_V26_N1_BLOCK_FEASIBILITY_DEGRADED_N1_SAMPLER_PENDING"
        or state.get("last_completed_task") != "S0_N1_BLOCK_FEASIBILITY"
        or state.get("recommended_next_task") != "S0_N1_SAMPLER"
        or state.get("last_run") != "runs/2026-08-24_017_n1_block_feasibility.md"
        or state.get("route", {}).get("locked") is not None
    ):
        _error(errors, "V26_PROJECT_STATE_MISMATCH", repr(project))

    blockers = {item.get("id"): item for item in state.get("blockers", []) if isinstance(item, dict)}
    superseded = {item.get("id"): item for item in state.get("superseded_blockers", []) if isinstance(item, dict)}
    b4 = blockers.get("B_V4_NULL_CONTRACT_UNVERIFIED")
    b9 = superseded.get("B_V9_A_FULL_OUTER_TRAIN_ADMISSION_PENDING")
    if "B_V9_A_FULL_OUTER_TRAIN_ADMISSION_PENDING" in blockers or not isinstance(b9, dict) or b9.get("closed_by") != "S0_A1_ADMISSION":
        _error(errors, "V26_B9_CLOSURE_MISMATCH", repr(b9))
    if not isinstance(b4, dict) or "S0_N1_SAMPLER" in b4.get("blocks", []) or "S0_N2_SAMPLER" not in b4.get("blocks", []):
        _error(errors, "V26_B4_BRANCH_RESOLVER_MISMATCH", repr(b4))

    for relative, expected in {**FROZEN_RUN_011_HASHES, **V26_FIXED_INPUT_HASHES, **V26_OUTPUT_HASHES}.items():
        path = root / relative
        if not path.is_file() or _sha256(path) != expected:
            _error(errors, "V26_ARTIFACT_HASH_MISMATCH", relative)
    for relative, expected, code in (
        ("scripts/audit_n1_block_feasibility.py", V26_FEASIBILITY_CODE_HASH, "V26_FEASIBILITY_CODE_HASH_MISMATCH"),
        ("tests/test_audit_n1_block_feasibility.py", V26_FEASIBILITY_TEST_HASH, "V26_FEASIBILITY_TEST_HASH_MISMATCH"),
    ):
        path = root / relative
        if not path.is_file() or _sha256(path) != expected:
            _error(errors, code, relative)

    artifact = _load_yaml(root / "artifacts/nulls/n1_block_feasibility.yaml", errors, "N1 block feasibility")
    expected_keys = [
        "schema_version", "artifact", "spec_version", "baseline_commit", "task", "policy_id",
        "evidence_scope", "input_artifacts", "authorized_scope", "power_proxy_contract",
        "length_bin_contract", "power_bin_contract", "block_contract", "permutation_probe_contract",
        "acceptance_thresholds", "acceptance_counts", "power_edges", "coverage",
        "block_size_distribution", "permutation_probe", "decision", "implementation",
        "prohibited", "safety", "downstream_boundary",
    ]
    if isinstance(artifact, dict):
        counts = artifact.get("acceptance_counts", {})
        coverage = artifact.get("coverage", {})
        blocks = artifact.get("block_size_distribution", {})
        probe = artifact.get("permutation_probe", {})
        decision = artifact.get("decision", {})
        safety = artifact.get("safety", {})
        boundary = artifact.get("downstream_boundary", {})
        replicates = probe.get("replicates", [])
        if (
            list(artifact) != expected_keys
            or artifact.get("artifact") != "RC_HSG_N1_BLOCK_FEASIBILITY_V1"
            or artifact.get("spec_version") != "v2.6"
            or artifact.get("baseline_commit") != "1c432a02f50cacda99359f630f14cfbfdfb439a1"
            or artifact.get("task") != "S0_N1_BLOCK_FEASIBILITY"
            or counts != {
                "outer_train_rows": 3541,
                "eligible_rows_read": 3497,
                "short_rows_no_read": 44,
                "full_windows": 35745,
                "subjects": 18,
                "source_files": 18,
                "source_dtype_counts": {"float64": 3497},
            }
            or coverage.get("minimum_subject_role_population_coverage") != 0.7777777777777778
            or coverage.get("exclusion_reason_counts") != {
                "N1_NOT_EVALUABLE_POWER_EDGE_UNAVAILABLE": 4,
                "N1_NOT_EVALUABLE_SHORT_FORCED_L0": 44,
                "N1_NOT_EVALUABLE_SINGLETON": 12,
            }
            or blocks.get("blocks") != 192
            or blocks.get("evaluable_blocks") != 180
            or blocks.get("singleton_blocks") != 12
            or len(replicates) != 199
            or probe.get("joint_mapping_unique_count") != 199
            or len({item.get("joint_mapping_sha256") for item in replicates if isinstance(item, dict)}) != 199
            or probe.get("bijection_violations") != 0
            or probe.get("cross_block_violations") != 0
            or decision != {
                "structural_status": "PASS",
                "decision": "DEGRADED_COVERAGE",
                "evidence_label": "N1_OUTER_TRAIN_BLOCK_FEASIBILITY_DEGRADED_COVERAGE",
                "primary_fallback_status": "INELIGIBLE_DUE_TO_OUTER_TRAIN_COVERAGE_BELOW_0_90",
                "next_task": "S0_N1_SAMPLER",
            }
            or safety != {
                "production_scan_attempts": 1,
                "eligible_arrays_read": 3497,
                "short_arrays_read": 0,
                "calibration_arrays_read": 0,
                "test_arrays_read": 0,
                "cpu_tokenizer_only": True,
                "full_encoder_executed": False,
                "row_proxy_persisted": False,
                "donor_eeg_read": False,
                "donor_map_persisted": False,
                "text_or_outcome_read": False,
                "training_or_parameter_update": False,
                "test_status": "LOCKED_UNTIL_ROUTE_LOCK",
            }
            or boundary != {
                "n1_block_feasibility_completed": True,
                "n1_sampler_implemented": False,
                "n2_sampler_implemented": False,
                "gate_r0_executed": False,
                "route_locked": False,
                "next_task": "S0_N1_SAMPLER",
            }
        ):
            _error(errors, "V26_FEASIBILITY_ARTIFACT_MISMATCH", "header, counts, coverage, blocks, probe, decision, safety, or boundary")

    ledger_path = root / "artifacts/nulls/n1_block_assignment_v1.jsonl"
    ledger: list[dict[str, Any]] = []
    try:
        for line_number, line in enumerate(ledger_path.read_text(encoding="utf-8").splitlines(), start=1):
            item = json.loads(line)
            if not isinstance(item, dict):
                raise ValueError(f"line {line_number} is not an object")
            ledger.append(item)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        _error(errors, "V26_LEDGER_INVALID", str(exc))
        ledger = []
    ledger_fields = [
        "subject", "session", "slot", "occurrence_id", "role", "raw_samples", "window_count",
        "a_interface_status", "action", "length_bin", "power_bin", "power_edge_cell_id",
        "power_edge_status", "block_id", "block_size", "n1_evaluable", "n1_status",
        "source_file", "source_field", "source_dataset_read_run017",
    ]
    if ledger:
        keys = [(item.get("subject"), item.get("slot"), item.get("occurrence_id")) for item in ledger]
        statuses = {
            label: sum(item.get("n1_status") == label for item in ledger)
            for label in (
                "N1_EVALUABLE", "N1_NOT_EVALUABLE_SHORT_FORCED_L0",
                "N1_NOT_EVALUABLE_SINGLETON", "N1_NOT_EVALUABLE_POWER_EDGE_UNAVAILABLE",
            )
        }
        if (
            len(ledger) != 3541
            or any(list(item) != ledger_fields for item in ledger)
            or keys != sorted(keys)
            or len(set(keys)) != 3541
            or statuses != {
                "N1_EVALUABLE": 3481,
                "N1_NOT_EVALUABLE_SHORT_FORCED_L0": 44,
                "N1_NOT_EVALUABLE_SINGLETON": 12,
                "N1_NOT_EVALUABLE_POWER_EDGE_UNAVAILABLE": 4,
            }
            or sum(item.get("source_dataset_read_run017") is True for item in ledger) != 3497
            or any(item.get("source_dataset_read_run017") is True for item in ledger if item.get("a_interface_status") == "SHORT_FORCED_L0")
            or any(item.get("role") not in {"train_fit", "inner_val"} or item.get("source_field") != "rawData" for item in ledger)
        ):
            _error(errors, "V26_LEDGER_MISMATCH", "schema, order, counts, reads, roles, or source field")

    split = _load_yaml(root / "artifacts/split_manifest.yaml", errors, "split manifest")
    if isinstance(split, dict) and split.get("assertions", {}).get("test_status") != "LOCKED_UNTIL_ROUTE_LOCK":
        _error(errors, "V26_TEST_LOCK_MISMATCH", repr(split.get("assertions", {}).get("test_status")))


def _check_v27_contract(root: Path, state: dict[str, Any], tasks: dict[str, Any], errors: list[str]) -> None:
    if state.get("project", {}).get("spec_version") != "v2.7":
        return

    status_counts = {
        status: sum(isinstance(task, dict) and task.get("status") == status for task in tasks.values())
        for status in ("DONE", "SKIPPED", "BLOCKED", "READY")
    }
    expected_statuses = {"DONE": 41, "SKIPPED": 8, "BLOCKED": 24, "READY": 1}
    if len(tasks) != 74 or status_counts != expected_statuses:
        _error(errors, "V27_TASK_STATE_MISMATCH", f"tasks={len(tasks)} statuses={status_counts!r}")
    ready = [task_id for task_id, task in tasks.items() if isinstance(task, dict) and task.get("status") == "READY"]
    if ready != ["S0_N2_SAMPLER"] or tasks.get("S0_N2_SAMPLER", {}).get("owner") != "CHATGPT_OR_AUTHOR":
        _error(errors, "V27_READY_SET_MISMATCH", repr(ready))
    if tasks.get("SPEC_V27_REVIEW", {}).get("status") != "DONE" or tasks.get("S0_N1_SAMPLER", {}).get("status") != "DONE":
        _error(errors, "V27_COMPLETED_CHAIN_MISMATCH", "SPEC_V27_REVIEW or S0_N1_SAMPLER")
    if tasks.get("SPEC_V27_REVIEW", {}).get("prerequisites") != ["SPEC_V26_REVIEW"]:
        _error(errors, "V27_SPEC_DEPENDENCY_MISMATCH", repr(tasks.get("SPEC_V27_REVIEW", {}).get("prerequisites")))

    project = state.get("project", {})
    if (
        project.get("spec_path") != "guide/RC_HSG_Paper_Spec_v2_7_2026-08-24.md"
        or project.get("baseline_commit") != "082ed4f72f1b8bbc18096a5f0caea2075b2783c4"
        or project.get("reviewed_commit") != "082ed4f72f1b8bbc18096a5f0caea2075b2783c4"
        or project.get("repository_status") != "RC_HSG_V27_N1_MECHANISM_SAMPLER_IMPLEMENTED_N2_PENDING"
        or state.get("last_completed_task") != "S0_N1_SAMPLER"
        or state.get("recommended_next_task") != "S0_N2_SAMPLER"
        or state.get("last_run") != "runs/2026-08-24_018_n1_mechanism_sampler.md"
        or state.get("route", {}).get("locked") is not None
    ):
        _error(errors, "V27_PROJECT_STATE_MISMATCH", repr(project))

    blockers = {item.get("id"): item for item in state.get("blockers", []) if isinstance(item, dict)}
    superseded = {item.get("id"): item for item in state.get("superseded_blockers", []) if isinstance(item, dict)}
    b4 = blockers.get("B_V4_NULL_CONTRACT_UNVERIFIED")
    b9 = superseded.get("B_V9_A_FULL_OUTER_TRAIN_ADMISSION_PENDING")
    if "B_V9_A_FULL_OUTER_TRAIN_ADMISSION_PENDING" in blockers or not isinstance(b9, dict) or b9.get("closed_by") != "S0_A1_ADMISSION":
        _error(errors, "V27_B9_CLOSURE_MISMATCH", repr(b9))
    if not isinstance(b4, dict) or "S0_N2_SAMPLER" in b4.get("blocks", []) or "GATE_R0" not in b4.get("blocks", []):
        _error(errors, "V27_B4_BRANCH_RESOLVER_MISMATCH", repr(b4))
    if any(
        not isinstance(gate, dict) or gate.get("status") != "BLOCKED" or gate.get("outcome") is not None
        for gate in state.get("gates", {}).values()
    ):
        _error(errors, "V27_GATE_STATE_MISMATCH", repr(state.get("gates")))

    frozen_hashes = {
        **FROZEN_RUN_011_HASHES,
        **V26_FIXED_INPUT_HASHES,
        **V26_OUTPUT_HASHES,
        **V27_FIXED_INPUT_HASHES,
        **V27_OUTPUT_HASHES,
    }
    for relative, expected in frozen_hashes.items():
        path = root / relative
        if not path.is_file() or _sha256(path) != expected:
            _error(errors, "V27_ARTIFACT_HASH_MISMATCH", relative)

    contract = _load_yaml(root / "artifacts/nulls/n1_contract.yaml", errors, "N1 sampler contract")
    expected_keys = [
        "schema_version", "artifact", "spec_version", "baseline_commit", "task", "policy_id",
        "evidence_scope", "input_artifacts", "assignment_scope", "permutation_contract", "parity",
        "selection_aware_boundary", "implementation", "outputs", "safety", "downstream_boundary",
    ]
    if isinstance(contract, dict):
        scope = contract.get("assignment_scope", {})
        permutation = contract.get("permutation_contract", {})
        parity = contract.get("parity", {})
        selection = contract.get("selection_aware_boundary", {})
        implementation = contract.get("implementation", {})
        safety = contract.get("safety", {})
        boundary = contract.get("downstream_boundary", {})
        if (
            list(contract) != expected_keys
            or contract.get("artifact") != "RC_HSG_N1_JOINT_PERMUTATION_SAMPLER_V1"
            or contract.get("spec_version") != "v2.7"
            or contract.get("baseline_commit") != "082ed4f72f1b8bbc18096a5f0caea2075b2783c4"
            or contract.get("task") != "S0_N1_SAMPLER"
            or scope != {
                "outer_train_rows": 3541,
                "evaluable_rows": 3481,
                "evaluable_blocks": 180,
                "excluded_rows": 60,
                "exclusion_counts": {"short_forced_l0": 44, "power_edge_unavailable": 4, "singleton": 12},
            }
            or permutation != {
                "replicates": 199,
                "algorithm": "SHA256_HASH_SORT_WITHIN_BLOCK_BIJECTION",
                "replicate_range": [1, 199],
                "fixed_points_retained": True,
                "adjacent_block_borrowing": False,
                "cross_scope_mapping": False,
                "rng_used": False,
                "python_hash_used": False,
            }
            or parity != {
                "replicates": 199,
                "exact_hash_matches": 199,
                "exact_fixed_point_matches": 199,
                "unique_joint_mapping_hashes": 199,
                "fixed_points_total": 35529,
                "fixed_points_min": 145,
                "fixed_points_max": 214,
                "bijection_violations": 0,
                "cross_block_violations": 0,
            }
            or selection != {
                "value_key_scope": "EXACT_3481_EVALUABLE_ROWS",
                "canonical_callback_calls_per_observation": 3481,
                "same_select_then_score_callback": True,
                "candidate_selection_recomputed": True,
                "parent_consistent_path_recomputed": True,
                "score_recomputed": True,
                "candidate_specific_shortcut": False,
                "paper_p_value_computed": False,
            }
            or implementation.get("module_sha256") != V27_IMPLEMENTATION_HASHES["src/rc_hsg/references/n1_joint_permutation.py"]
            or implementation.get("builder_sha256") != V27_IMPLEMENTATION_HASHES["scripts/build_n1_sampler_contract.py"]
            or implementation.get("feasibility_script_imported") is not False
            or implementation.get("frontend_or_a1_imported") is not False
            or safety != {
                "metadata_only": True,
                "production_eeg_reads": 0,
                "short_array_reads": 0,
                "calibration_array_reads": 0,
                "test_array_reads": 0,
                "text_or_outcome_reads": 0,
                "frontend_or_tokenizer_loads": 0,
                "proxy_token_embedding_waveform_reads": 0,
                "mapping_relations_persisted": False,
                "semantic_candidate_or_reference_score_generated": False,
                "donor_value_generated": False,
                "paper_p_value_computed": False,
                "test_status": "LOCKED_UNTIL_ROUTE_LOCK",
            }
            or boundary != {
                "n1_mechanism_sampler_implemented": True,
                "n1_primary_admitted": False,
                "n2_sampler_implemented": False,
                "gate_r0_executed": False,
                "route_locked": False,
                "next_task": "S0_N2_SAMPLER",
                "next_owner": "CHATGPT_OR_AUTHOR",
            }
        ):
            _error(errors, "V27_N1_CONTRACT_MISMATCH", "schema, scope, permutation, parity, selection, safety, or boundary")

    manifest_path = root / "artifacts/nulls/n1_permutation_manifest_v1.jsonl"
    manifest: list[dict[str, Any]] = []
    try:
        for line_number, line in enumerate(manifest_path.read_text(encoding="utf-8").splitlines(), start=1):
            item = json.loads(line)
            if not isinstance(item, dict):
                raise ValueError(f"line {line_number} is not an object")
            manifest.append(item)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        _error(errors, "V27_MANIFEST_INVALID", str(exc))
        manifest = []
    manifest_fields = [
        "replicate_id", "policy_id", "evaluable_rows", "evaluable_blocks",
        "fixed_points", "fixed_point_rate", "joint_mapping_sha256",
    ]
    if manifest:
        fixed_points = [item.get("fixed_points") for item in manifest]
        hashes = [item.get("joint_mapping_sha256") for item in manifest]
        if (
            len(manifest) != 199
            or any(list(item) != manifest_fields for item in manifest)
            or [item.get("replicate_id") for item in manifest] != list(range(1, 200))
            or any(item.get("policy_id") != "RC_HSG_N1_JOINT_PERMUTATION_SAMPLER_V1" for item in manifest)
            or any(item.get("evaluable_rows") != 3481 or item.get("evaluable_blocks") != 180 for item in manifest)
            or any(not isinstance(value, int) for value in fixed_points)
            or sum(fixed_points) != 35529
            or min(fixed_points) != 145
            or max(fixed_points) != 214
            or len(set(hashes)) != 199
            or any(not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{64}", value) is None for value in hashes)
            or any(item.get("fixed_point_rate") != f"{item['fixed_points'] / 3481:.12f}" for item in manifest)
        ):
            _error(errors, "V27_MANIFEST_MISMATCH", "schema, IDs, scope, fixed points, rates, or hashes")

    forbidden_fields = (
        b"recipient_row_key", b"donor_row_key", b"eeg_value", b"token_value",
        b"embedding_value", b"proxy_value", b"waveform_value", b'"donor":',
        b'"recipient":', b"stimulus_text", b"outcome_value",
    )
    for relative in V27_OUTPUT_HASHES:
        path = root / relative
        try:
            payload = path.read_bytes().lower()
        except OSError:
            continue
        if len(payload) > 500_000 or any(field in payload for field in forbidden_fields):
            _error(errors, "V27_PERSISTENCE_FIREWALL_MISMATCH", relative)

    split = _load_yaml(root / "artifacts/split_manifest.yaml", errors, "split manifest")
    if isinstance(split, dict) and split.get("assertions", {}).get("test_status") != "LOCKED_UNTIL_ROUTE_LOCK":
        _error(errors, "V27_TEST_LOCK_MISMATCH", repr(split.get("assertions", {}).get("test_status")))


def _check_v28_contract(root: Path, state: dict[str, Any], tasks: dict[str, Any], errors: list[str]) -> None:
    if state.get("project", {}).get("spec_version") != "v2.8":
        return

    status_counts = {
        status: sum(isinstance(task, dict) and task.get("status") == status for task in tasks.values())
        for status in ("DONE", "SKIPPED", "BLOCKED", "READY")
    }
    expected_statuses = {"DONE": 43, "SKIPPED": 8, "BLOCKED": 23, "READY": 1}
    if len(tasks) != 75 or status_counts != expected_statuses:
        _error(errors, "V28_TASK_STATE_MISMATCH", f"tasks={len(tasks)} statuses={status_counts!r}")
    ready = [task_id for task_id, task in tasks.items() if isinstance(task, dict) and task.get("status") == "READY"]
    if ready != ["GATE_R0"] or tasks.get("GATE_R0", {}).get("owner") != "CHATGPT_OR_AUTHOR":
        _error(errors, "V28_READY_SET_MISMATCH", repr(ready))
    if tasks.get("SPEC_V28_REVIEW", {}).get("status") != "DONE" or tasks.get("S0_N2_SAMPLER", {}).get("status") != "DONE":
        _error(errors, "V28_COMPLETED_CHAIN_MISMATCH", "SPEC_V28_REVIEW or S0_N2_SAMPLER")
    if tasks.get("SPEC_V28_REVIEW", {}).get("prerequisites") != ["SPEC_V27_REVIEW"]:
        _error(errors, "V28_SPEC_DEPENDENCY_MISMATCH", repr(tasks.get("SPEC_V28_REVIEW", {}).get("prerequisites")))

    project = state.get("project", {})
    execution = state.get("execution", {})
    if (
        project.get("spec_path") != "guide/RC_HSG_Paper_Spec_v2_8_2026-08-24.md"
        or project.get("baseline_commit") != "06e3e5f9b5c720bbb29074ca1cae1109add5b1b9"
        or project.get("reviewed_commit") != "06e3e5f9b5c720bbb29074ca1cae1109add5b1b9"
        or project.get("repository_status") != "RC_HSG_V28_N2_COMMON_PHASE_SAMPLER_IMPLEMENTED_GATE_R0_AUDIT_PENDING"
        or execution != {"stage": "gate_r0", "status": "READY", "current_gate": "gate_r0"}
        or state.get("last_completed_task") != "S0_N2_SAMPLER"
        or state.get("recommended_next_task") != "GATE_R0"
        or state.get("last_run") != "runs/2026-08-24_019_n2_common_phase_sampler.md"
        or state.get("route", {}).get("locked") is not None
    ):
        _error(errors, "V28_PROJECT_STATE_MISMATCH", repr(project))

    blockers = {item.get("id"): item for item in state.get("blockers", []) if isinstance(item, dict)}
    superseded = {item.get("id"): item for item in state.get("superseded_blockers", []) if isinstance(item, dict)}
    b4 = blockers.get("B_V4_NULL_CONTRACT_UNVERIFIED")
    b9 = superseded.get("B_V9_A_FULL_OUTER_TRAIN_ADMISSION_PENDING")
    if "B_V9_A_FULL_OUTER_TRAIN_ADMISSION_PENDING" in blockers or not isinstance(b9, dict) or b9.get("closed_by") != "S0_A1_ADMISSION":
        _error(errors, "V28_B9_CLOSURE_MISMATCH", repr(b9))
    if (
        not isinstance(b4, dict)
        or "GATE_R0" in b4.get("blocks", [])
        or "S0_ALIGN_UNIT_COST" not in b4.get("blocks", [])
        or "S0_REFERENCE_FEATURES" not in b4.get("blocks", [])
        or "MECHANISM_A" not in b4.get("blocks", [])
    ):
        _error(errors, "V28_B4_BRANCH_RESOLVER_MISMATCH", repr(b4))
    gates = state.get("gates", {})
    expected_gates = {
        "gate_r0": {"status": "READY", "outcome": None},
        "gate_r": {"status": "BLOCKED", "outcome": None},
        "gate_c": {"status": "BLOCKED", "outcome": None},
        "gate_h": {"status": "BLOCKED", "outcome": None},
        "mechanism_a": {"status": "BLOCKED", "outcome": None},
    }
    if gates != expected_gates:
        _error(errors, "V28_GATE_STATE_MISMATCH", repr(gates))

    frozen_hashes = {
        **FROZEN_RUN_011_HASHES,
        **V26_FIXED_INPUT_HASHES,
        **V26_OUTPUT_HASHES,
        **V27_FIXED_INPUT_HASHES,
        **V27_IMPLEMENTATION_HASHES,
        **V27_OUTPUT_HASHES,
        **V28_FIXED_INPUT_HASHES,
        **V28_IMPLEMENTATION_HASHES,
        **V28_OUTPUT_HASHES,
    }
    for relative, expected in frozen_hashes.items():
        path = root / relative
        if not path.is_file() or _sha256(path) != expected:
            _error(errors, "V28_ARTIFACT_HASH_MISMATCH", relative)

    correction = _load_yaml(
        root / "artifacts/governance/run018_provenance_correction.yaml",
        errors,
        "run-018 provenance correction",
    )
    if isinstance(correction, dict) and correction != {
        "schema_version": 1,
        "artifact": "RC_HSG_RUN018_PROVENANCE_CORRECTION_V1",
        "created_by_run": "2026-08-24_019_n2_common_phase_sampler",
        "historical_run": {
            "path": "runs/2026-08-24_018_n1_mechanism_sampler.md",
            "sha256": "0b3f9ee0662f3429b3ac6fe0b78148e5b61aa2de21d59bec97f8cc634b90d4e7",
            "modified": False,
        },
        "field": "package_source_CODEX_NEXT_TASK_sha256",
        "recorded_sha256": "667b36d04a5e91fd314bf44b1e7ce0a145ed0e9a45286c36c56c8eb8c9d2b0e7",
        "corrected_sha256": "667b8bc2af414673e09d9d2011446db502fbca305fb26e6c558bd0a762d51ef6",
        "source_zip_sha256": "934d7bb625b6a5183d251ae0d7b5255053adaebef17a0883394a371f3f5b5c24",
        "verification_basis": "ZIP_CONTENT_AND_PACKAGE_MANIFEST_SHA256",
        "scientific_state_changed": False,
        "code_artifact_test_state_changed": False,
    }:
        _error(errors, "V28_PROVENANCE_CORRECTION_MISMATCH", "schema or correction values")

    contract = _load_yaml(root / "artifacts/nulls/n2_contract.yaml", errors, "N2 sampler contract")
    expected_keys = [
        "schema_version", "artifact", "spec_version", "baseline_commit", "task", "policy_id",
        "evidence_scope", "input_artifacts", "scientific_basis", "transform_contract",
        "seed_contract", "input_output_contract", "synthetic_fixtures", "preservation_thresholds",
        "synthetic_diagnostics", "artifact_diagnostics_schema", "implementation", "prohibited",
        "safety", "downstream_boundary",
    ]
    if isinstance(contract, dict):
        transform = contract.get("transform_contract", {})
        seed = contract.get("seed_contract", {})
        fixtures = contract.get("synthetic_fixtures", {})
        thresholds = contract.get("preservation_thresholds", {})
        diagnostics = contract.get("synthetic_diagnostics", {})
        implementation = contract.get("implementation", {})
        safety = contract.get("safety", {})
        boundary = contract.get("downstream_boundary", {})
        cases = diagnostics.get("cases", [])
        preservation_labels = (
            "psd_relative_norm", "covariance_relative_norm", "mean_relative_norm",
            "cross_spectrum_relative_norm",
        )
        parsed_metrics: list[float] = []
        metric_parse_failed = False
        try:
            for case in cases:
                parsed_metrics.extend(float.fromhex(case["metrics"][label]) for label in preservation_labels)
        except (KeyError, TypeError, ValueError):
            metric_parse_failed = True
        if (
            list(contract) != expected_keys
            or contract.get("artifact") != "RC_HSG_N2_MULTIVARIATE_COMMON_PHASE_FOURIER_V1"
            or contract.get("spec_version") != "v2.8"
            or contract.get("baseline_commit") != "06e3e5f9b5c720bbb29074ca1cae1109add5b1b9"
            or contract.get("task") != "S0_N2_SAMPLER"
            or transform.get("channels") != 105
            or transform.get("minimum_valid_samples") != 500
            or transform.get("input_device") != "CPU"
            or transform.get("input_dtype") != "torch.float32"
            or transform.get("fft_internal_dtype") != "numpy.float64"
            or transform.get("output_dtype") != "torch.float32"
            or transform.get("common_phase_across_channels") is not True
            or transform.get("dc_fixed") is not True
            or transform.get("even_nyquist_fixed") is not True
            or transform.get("valid_unpadded_prefix_only") is not True
            or transform.get("padding_tail_exact_zero") is not True
            or seed.get("replicates") != 199
            or seed.get("replicate_range") != [1, 199]
            or seed.get("replicate_encoding") != "UINT16_BIG_ENDIAN"
            or seed.get("generator") != "numpy.random.Generator(PCG64(seed))@2.5.2"
            or seed.get("global_rng_state_used") is not False
            or fixtures.get("lengths") != [500, 501, 513, 2048, 27010]
            or fixtures.get("grid_replicates") != [1, 2, 199]
            or fixtures.get("all_pair_count") != 11025
            or any(float.fromhex(value) != 1e-6 for key, value in thresholds.items() if key.endswith("_max"))
            or diagnostics.get("grid_cases") != 15
            or diagnostics.get("all_preservation_checks_pass") is not True
            or not isinstance(cases, list)
            or len(cases) != 15
            or [(case.get("valid_samples"), case.get("replicate_id")) for case in cases]
            != [(length, replicate) for length in (500, 501, 513, 2048, 27010) for replicate in (1, 2, 199)]
            or len({case.get("phase_seed_sha256") for case in cases}) != 15
            or metric_parse_failed
            or len(parsed_metrics) != 60
            or any(not isinstance(value, float) or value < 0.0 or value > 1e-6 for value in parsed_metrics)
            or diagnostics.get("replicate_replay") != {
                "replicates": 199,
                "unique_seed_hashes": 199,
                "unique_output_fingerprints": 199,
                "finite_outputs": 199,
                "bitwise_replay": True,
            }
            or diagnostics.get("padded_fixture") != {
                "rows": 2,
                "valid_samples": [513, 501],
                "prefix_unpadded_bitwise_equal": True,
                "mask_exact": True,
                "padding_tail_exact_zero": True,
                "nonfinite_padding_ignored": True,
            }
            or implementation.get("module_sha256") != V28_IMPLEMENTATION_HASHES["src/rc_hsg/references/n2_common_phase.py"]
            or implementation.get("builder_sha256") != V28_IMPLEMENTATION_HASHES["scripts/build_n2_sampler_contract.py"]
            or implementation.get("numpy_version") != "2.5.2"
            or safety != {
                "synthetic_only": True,
                "real_outer_train_reads": 0,
                "calibration_reads": 0,
                "test_reads": 0,
                "text_outcome_test_identity_reads": 0,
                "a1_frontend_encoder_loads": 0,
                "embedding_reference_score_p_value_generated": 0,
                "training_or_classifier_runs": 0,
                "fixture_waveform_fft_phase_seed_integer_persisted": False,
                "test_status": "LOCKED_UNTIL_ROUTE_LOCK",
            }
            or boundary != {
                "n2_sampler_implemented": True,
                "n2_primary_admitted": False,
                "gate_r0_executed": False,
                "route_locked": False,
                "next_task": "GATE_R0",
                "next_owner": "CHATGPT_OR_AUTHOR",
            }
        ):
            _error(errors, "V28_N2_CONTRACT_MISMATCH", "header, transform, seed, diagnostics, safety, or boundary")

    forbidden_fields = (
        b"waveform_values", b"fft_values", b"phase_angles", b"seed_integer:",
        b"eeg_values", b"embedding_values", b"reference_scores", b"outcome_values",
        b"stimulus_text", b"dataset_root",
    )
    for relative in V28_OUTPUT_HASHES:
        path = root / relative
        try:
            payload = path.read_bytes().lower()
        except OSError:
            continue
        if len(payload) > 500_000 or any(field in payload for field in forbidden_fields):
            _error(errors, "V28_PERSISTENCE_FIREWALL_MISMATCH", relative)

    split = _load_yaml(root / "artifacts/split_manifest.yaml", errors, "split manifest")
    if isinstance(split, dict) and split.get("assertions", {}).get("test_status") != "LOCKED_UNTIL_ROUTE_LOCK":
        _error(errors, "V28_TEST_LOCK_MISMATCH", repr(split.get("assertions", {}).get("test_status")))


def _check_v293_contract(root: Path, state: dict[str, Any], tasks: dict[str, Any], errors: list[str]) -> None:
    if state.get("project", {}).get("spec_version") != "v2.9.3":
        return

    status_counts = {
        status: sum(isinstance(task, dict) and task.get("status") == status for task in tasks.values())
        for status in ("DONE", "SKIPPED", "BLOCKED", "READY")
    }
    if len(tasks) != 79 or status_counts != {"DONE": 48, "SKIPPED": 8, "BLOCKED": 22, "READY": 1}:
        _error(errors, "V293_TASK_STATE_MISMATCH", f"tasks={len(tasks)} statuses={status_counts!r}")
    ready = [task_id for task_id, task in tasks.items() if isinstance(task, dict) and task.get("status") == "READY"]
    if ready != ["S0_SEMANTIC_ITEM"] or tasks.get("S0_SEMANTIC_ITEM", {}).get("owner") != "CHATGPT_OR_AUTHOR":
        _error(errors, "V293_READY_SET_MISMATCH", repr(ready))
    review_chain = (
        ("SPEC_V29_REVIEW", ["SPEC_V28_REVIEW"]),
        ("SPEC_V291_REVIEW", ["SPEC_V29_REVIEW"]),
        ("SPEC_V292_REVIEW", ["SPEC_V291_REVIEW"]),
        ("SPEC_V293_REVIEW", ["SPEC_V292_REVIEW"]),
    )
    for task_id, prerequisites in review_chain:
        task = tasks.get(task_id, {})
        if task.get("status") != "DONE" or task.get("prerequisites") != prerequisites:
            _error(errors, "V293_SPEC_CHAIN_MISMATCH", f"{task_id}:{task!r}")
    if tasks.get("GATE_R0", {}).get("status") != "DONE":
        _error(errors, "V293_GATE_TASK_MISMATCH", repr(tasks.get("GATE_R0")))

    project = state.get("project", {})
    if (
        project.get("spec_path") != "guide/RC_HSG_Paper_Spec_v2_9_3_2026-08-24.md"
        or project.get("baseline_commit") != "4fa6fadc8bdee0d163acc8bf9ee48aeac4d3095d"
        or project.get("reviewed_commit") != "4fa6fadc8bdee0d163acc8bf9ee48aeac4d3095d"
        or project.get("repository_status") != "RC_HSG_V29_GATE_R0_FAILED_ORDINARY_HSG_SCHEMA_REVIEW_PENDING"
        or state.get("execution") != {"stage": "stage_0", "status": "READY", "current_gate": None}
        or state.get("last_completed_task") != "GATE_R0"
        or state.get("recommended_next_task") != "S0_SEMANTIC_ITEM"
        or state.get("last_run") != "runs/2026-08-24_020_gate_r0_reference_integrity.md"
    ):
        _error(errors, "V293_PROJECT_STATE_MISMATCH", repr(project))
    route = state.get("route", {})
    if route.get("primary") != "ORDINARY_HIERARCHICAL_SELECTIVE_GENERATION" or route.get("locked") is not None:
        _error(errors, "V293_ROUTE_STATE_MISMATCH", repr(route))
    expected_gates = {
        "gate_r0": {"status": "DONE", "outcome": "FAIL_NO_PRIMARY_REFERENCE"},
        "gate_r": {"status": "BLOCKED", "outcome": None},
        "gate_c": {"status": "BLOCKED", "outcome": None},
        "gate_h": {"status": "BLOCKED", "outcome": None},
        "mechanism_a": {"status": "BLOCKED", "outcome": None},
    }
    if state.get("gates") != expected_gates:
        _error(errors, "V293_GATE_STATE_MISMATCH", repr(state.get("gates")))

    blockers = {item.get("id"): item for item in state.get("blockers", []) if isinstance(item, dict)}
    superseded = {item.get("id"): item for item in state.get("superseded_blockers", []) if isinstance(item, dict)}
    b3 = blockers.get("B_V3_SCHEMA_UNFROZEN", {})
    b4 = superseded.get("B_V4_NULL_CONTRACT_UNVERIFIED", {})
    b9 = superseded.get("B_V9_A_FULL_OUTER_TRAIN_ADMISSION_PENDING", {})
    if "S0_SEMANTIC_ITEM" in b3.get("blocks", []):
        _error(errors, "V293_B3_RESOLVER_MISMATCH", repr(b3))
    if "B_V4_NULL_CONTRACT_UNVERIFIED" in blockers or b4.get("closed_by") != "GATE_R0":
        _error(errors, "V293_B4_CLOSURE_MISMATCH", repr(b4))
    if "B_V9_A_FULL_OUTER_TRAIN_ADMISSION_PENDING" in blockers or b9.get("closed_by") != "S0_A1_ADMISSION":
        _error(errors, "V293_B9_CLOSURE_MISMATCH", repr(b9))

    frozen_hashes = {
        **FROZEN_RUN_011_HASHES,
        **V26_FIXED_INPUT_HASHES,
        **V26_OUTPUT_HASHES,
        **V27_FIXED_INPUT_HASHES,
        **V27_IMPLEMENTATION_HASHES,
        **V27_OUTPUT_HASHES,
        **V28_FIXED_INPUT_HASHES,
        **V28_IMPLEMENTATION_HASHES,
        **V28_OUTPUT_HASHES,
        **V293_FIXED_HASHES,
    }
    for relative, expected in frozen_hashes.items():
        path = root / relative
        if not path.is_file() or _sha256(path) != expected:
            _error(errors, "V293_ARTIFACT_HASH_MISMATCH", relative)

    gate = _load_yaml(root / "artifacts/gates/gate_r0.yaml", errors, "Gate R0 artifact")
    if isinstance(gate, dict):
        reads = gate.get("read_counters", {})
        diagnostics = gate.get("model_fit_diagnostics", {})
        expected_zero = (
            "short_arrays", "calibration_arrays", "test_arrays", "text_reads",
            "outcome_reads", "test_identity_reads", "n1_real_eeg_reads",
        )
        if (
            gate.get("spec_version") != "v2.9.3"
            or gate.get("decision") != "FAIL_NO_PRIMARY_REFERENCE"
            or gate.get("n2_primary") != "NOT_ADMITTED"
            or reads.get("eligible_outer_train_arrays") != 3497
            or reads.get("full_audit_arrays") != 3497
            or reads.get("matched_panel_arrays") != 176
            or any(reads.get(key) != 0 for key in expected_zero)
            or gate.get("support", {}).get("ledger_sha256") != "3f2eb411e54c730453d1dd8a39c5bfeff0aa34ee278c545ac66d2f24b2af2246"
            or gate.get("panel", {}).get("sha256") != "2cffa7699e7a29eee4996172a20707678ba1ec3529d35e32b2ca453ad79aa806"
            or gate.get("model_api_certificate_sha256") != "0f9d4232922588a8a9859ad64b6e122362e79f1ae6c0123cf1ce8b0d40b5af34"
            or diagnostics.get("all_production_warning_counts_zero") is not True
            or gate.get("test_status") != "LOCKED_UNTIL_ROUTE_LOCK"
            or gate.get("route_locked") is not False
        ):
            _error(errors, "V293_GATE_ARTIFACT_MISMATCH", "scope, decision, reads, model, or lock")


def validate(root: Path) -> list[str]:
    root = root.resolve()
    errors: list[str] = []
    state_path = root / "PROJECT_STATE.yaml"
    tasks_path = root / "TASKS.yaml"
    state = _load_yaml(state_path, errors, "PROJECT_STATE.yaml")
    tasks = _load_yaml(tasks_path, errors, "TASKS.yaml")
    if not isinstance(state, dict) or not isinstance(tasks, dict):
        return errors

    missing_ids = sorted(REQUIRED_TASK_IDS - set(tasks))
    if missing_ids:
        _error(errors, "REQUIRED_TASK_MISSING", ", ".join(missing_ids))

    blockers = state.get("blockers", [])
    if not isinstance(blockers, list):
        _error(errors, "BLOCKERS_NOT_LIST", "PROJECT_STATE.blockers")
        blockers = []
    blocked_ids: set[str] = set()
    for index, blocker in enumerate(blockers):
        if not isinstance(blocker, dict):
            _error(errors, "BLOCKER_INVALID", f"index {index} is not a mapping")
            continue
        for field in ("id", "reason", "blocks", "resolution"):
            value = blocker.get(field)
            if value is None or value == "" or value == []:
                _error(
                    errors,
                    "BLOCKER_FIELD_MISSING",
                    f"blocker {blocker.get('id', index)!r}: {field}",
                )
        blocks = blocker.get("blocks", [])
        if not isinstance(blocks, list):
            _error(errors, "BLOCKER_BLOCKS_NOT_LIST", str(blocker.get("id", index)))
            continue
        for task_id in blocks:
            if task_id not in tasks:
                _error(
                    errors,
                    "BLOCKER_UNKNOWN_TASK",
                    f"{blocker.get('id')}: {task_id}",
                )
            elif isinstance(task_id, str):
                blocked_ids.add(task_id)

    for task_id, task in tasks.items():
        if not isinstance(task, dict):
            _error(errors, "TASK_NOT_MAPPING", task_id)
            continue
        missing_fields = sorted(REQUIRED_TASK_FIELDS - set(task))
        if missing_fields:
            _error(
                errors,
                "TASK_FIELD_MISSING",
                f"{task_id}: {', '.join(missing_fields)}",
            )
        status = task.get("status")
        if status not in ALLOWED_STATUSES:
            _error(errors, "ILLEGAL_STATUS", f"{task_id}: {status!r}")
        for field in ("prerequisites", "produces", "acceptance"):
            if field in task and not isinstance(task[field], list):
                _error(errors, "TASK_FIELD_NOT_LIST", f"{task_id}.{field}")
        prerequisites = task.get("prerequisites", [])
        if isinstance(prerequisites, list):
            for prerequisite in prerequisites:
                if prerequisite not in tasks:
                    _error(
                        errors,
                        "UNKNOWN_PREREQUISITE",
                        f"{task_id}: {prerequisite}",
                    )

        prerequisites_done = _prerequisites_done(task, tasks)
        if status == "READY":
            if not prerequisites_done:
                _error(errors, "READY_PREREQUISITE_NOT_DONE", task_id)
            if task_id in blocked_ids:
                _error(errors, "READY_BLOCKED", task_id)
            if task_id == "S0_A_INTERFACE" and task.get("owner") != "CODEX":
                _error(errors, "A_INTERFACE_OWNER_MISMATCH", task_id)
        elif status == "DONE":
            if not prerequisites_done:
                _error(errors, "DONE_PREREQUISITE_NOT_DONE", task_id)
            completed_by_run = task.get("completed_by_run")
            run_path = _run_record_path(root, completed_by_run)
            if run_path is None:
                _error(errors, "DONE_RUN_MISSING", f"{task_id}: completed_by_run")
            elif not run_path.is_file():
                _error(errors, "DONE_RUN_MISSING", f"{task_id}: {run_path}")
            produces = task.get("produces", [])
            if isinstance(produces, list):
                for artifact in produces:
                    artifact_path = _safe_relative_path(root, artifact)
                    if artifact_path is None:
                        _error(errors, "ARTIFACT_PATH_INVALID", f"{task_id}: {artifact!r}")
                    elif not artifact_path.exists():
                        _error(errors, "DONE_ARTIFACT_MISSING", f"{task_id}: {artifact}")
            evidence = task.get("acceptance_evidence")
            if not isinstance(evidence, list) or not evidence:
                _error(errors, "DONE_ACCEPTANCE_EVIDENCE_MISSING", task_id)
            else:
                valid_evidence: list[str] = []
                for item in evidence:
                    evidence_path = _safe_relative_path(root, item)
                    if evidence_path is None:
                        _error(
                            errors,
                            "DONE_ACCEPTANCE_EVIDENCE_PATH_INVALID",
                            f"{task_id}: {item!r}",
                        )
                    elif not evidence_path.exists():
                        _error(
                            errors,
                            "DONE_ACCEPTANCE_EVIDENCE_MISSING_PATH",
                            f"{task_id}: {item}",
                        )
                    else:
                        valid_evidence.append(str(item))
                non_run = [item for item in valid_evidence if not item.startswith("runs/")]
                if not non_run and any(not str(item).startswith("runs/") for item in produces):
                    _error(errors, "DONE_ACCEPTANCE_EVIDENCE_MISSING", f"{task_id}: run-only evidence")
        elif status == "BLOCKED":
            if not isinstance(task.get("blocked_reason"), str) or not task.get(
                "blocked_reason", ""
            ).strip():
                _error(errors, "BLOCKED_REASON_MISSING", task_id)
            optional_native_a_deferral = (
                state.get("project", {}).get("spec_version") in {"v2.5", "v2.6", "v2.7", "v2.8", "v2.9.3"}
                and task_id == "S0_A3_CONTAMINATION_CHECK"
                and task.get("critical_path") is False
            )
            post_gate_r0_fail_deferral = (
                state.get("project", {}).get("spec_version") == "v2.9.3"
                and task_id == "S0_ALIGN_UNIT_COST"
            )
            if (
                prerequisites_done
                and task_id not in blocked_ids
                and not optional_native_a_deferral
                and not post_gate_r0_fail_deferral
            ):
                _error(
                    errors,
                    "BLOCKED_WITHOUT_CAUSE",
                    f"{task_id}: prerequisites are DONE and no active blocker names it",
                )

    _check_cycles(tasks, errors)
    _check_gate_order(tasks, errors)
    _check_v21_contract(root, state, tasks, errors)
    _check_v22_contract(root, state, tasks, errors)
    _check_v23_contract(root, state, tasks, errors)
    _check_v24_contract(root, state, tasks, errors)
    _check_v25_contract(root, state, tasks, errors)
    _check_v26_contract(root, state, tasks, errors)
    _check_v27_contract(root, state, tasks, errors)
    _check_v28_contract(root, state, tasks, errors)
    _check_v293_contract(root, state, tasks, errors)

    project = state.get("project")
    if not isinstance(project, dict):
        _error(errors, "PROJECT_SECTION_INVALID", "project must be a mapping")
        project = {}
    _check_active_spec_entrypoints(root, project, errors)
    for field, code in (
        ("spec_path", "SPEC_PATH_INVALID"),
        ("management_contract_path", "MANAGEMENT_CONTRACT_PATH_INVALID"),
    ):
        path = _safe_relative_path(root, project.get(field))
        if path is None or not path.is_file():
            _error(errors, code, repr(project.get(field)))
    spec_version = project.get("spec_version")
    spec_path_value = project.get("spec_path", "")
    spec_path = _safe_relative_path(root, spec_path_value)
    spec_header = ""
    if spec_path is not None and spec_path.is_file():
        try:
            with spec_path.open("r", encoding="utf-8") as handle:
                spec_header = "".join(handle.readline() for _ in range(5))
        except OSError:
            pass
    version_token = spec_version.replace(".", "_") if isinstance(spec_version, str) else ""
    cumulative_v293_spec = (
        spec_version == "v2.9.3"
        and spec_path_value == "guide/RC_HSG_Paper_Spec_v2_9_3_2026-08-24.md"
        and spec_path is not None
        and spec_path.is_file()
        and _sha256(spec_path) == V293_FIXED_HASHES[spec_path_value]
    )
    if (
        not isinstance(spec_version, str)
        or SPEC_VERSION_RE.fullmatch(spec_version) is None
        or version_token not in Path(str(spec_path_value)).name
        or (spec_version not in spec_header and not cumulative_v293_spec)
    ):
        _error(
            errors,
            "SPEC_VERSION_MISMATCH",
            f"version={spec_version!r}, path={spec_path_value!r}",
        )
    if COMMIT_RE.fullmatch(str(project.get("reviewed_commit", ""))) is None:
        _error(errors, "REVIEWED_COMMIT_INVALID", repr(project.get("reviewed_commit")))

    execution = state.get("execution", {})
    if not isinstance(execution, dict) or execution.get("status") not in ALLOWED_STATUSES:
        _error(
            errors,
            "EXECUTION_STATUS_INVALID",
            repr(execution.get("status") if isinstance(execution, dict) else execution),
        )

    gates = state.get("gates", {})
    if not isinstance(gates, dict):
        _error(errors, "GATES_SECTION_INVALID", "gates must be a mapping")
        gates = {}
    for key, task_id in V21_ACTIVE_GATES.items():
        gate = gates.get(key, {})
        if not isinstance(gate, dict):
            _error(errors, "GATE_INVALID", key)
            continue
        if gate.get("status") not in ALLOWED_STATUSES:
            _error(errors, "GATE_STATUS_INVALID", f"{key}: {gate.get('status')!r}")
        if gate.get("outcome") not in ALLOWED_GATE_OUTCOMES:
            _error(errors, "GATE_OUTCOME_INVALID", f"{key}: {gate.get('outcome')!r}")
        task_status = tasks.get(task_id, {}).get("status")
        if gate.get("status") != task_status:
            _error(
                errors,
                "GATE_TASK_STATUS_MISMATCH",
                f"{key}={gate.get('status')!r}, {task_id}={task_status!r}",
            )
        if task_status == "DONE" and gate.get("outcome") is None:
            _error(errors, "GATE_OUTCOME_REQUIRED", task_id)
        if task_status != "DONE" and gate.get("outcome") is not None:
            _error(errors, "PREMATURE_GATE_OUTCOME", task_id)

    route = state.get("route", {})
    if not isinstance(route, dict):
        _error(errors, "ROUTE_SECTION_INVALID", "route must be a mapping")
        route = {}
    locked = route.get("locked")
    route_lock_done = tasks.get("ROUTE_LOCK", {}).get("status") == "DONE"
    if isinstance(locked, list):
        if len(locked) > 1:
            _error(errors, "MULTIPLE_ROUTES_LOCKED", repr(locked))
        locked_values = set(locked)
    elif locked is None:
        locked_values = set()
    elif isinstance(locked, str):
        locked_values = {locked} if locked else set()
    else:
        _error(errors, "ROUTE_LOCK_INVALID", repr(locked))
        locked_values = set()
    illegal_routes = locked_values - ALLOWED_LOCKED_ROUTES
    if illegal_routes:
        _error(errors, "ROUTE_VALUE_INVALID", repr(sorted(illegal_routes)))
    locked_by_run = route.get("locked_by_run")
    if route_lock_done:
        if not isinstance(locked, str) or not locked:
            _error(errors, "ROUTE_LOCK_REQUIRED", repr(locked))
        if not isinstance(locked_by_run, str) or not locked_by_run.strip():
            _error(errors, "ROUTE_LOCK_RUN_MISSING", repr(locked_by_run))
        else:
            lock_run_path = _run_record_path(root, locked_by_run)
            if lock_run_path is None or not lock_run_path.is_file():
                _error(errors, "ROUTE_LOCK_RUN_MISSING", repr(locked_by_run))
    else:
        if locked_values:
            _error(errors, "ROUTE_LOCK_PREMATURE", repr(sorted(locked_values)))
        if locked_by_run not in (None, ""):
            _error(errors, "ROUTE_LOCK_PREMATURE", f"locked_by_run={locked_by_run!r}")

    last_completed = state.get("last_completed_task")
    if last_completed is not None and tasks.get(last_completed, {}).get("status") != "DONE":
        _error(errors, "LAST_COMPLETED_NOT_DONE", repr(last_completed))
    last_run = _safe_relative_path(root, state.get("last_run"))
    if last_run is None or not last_run.is_file():
        _error(errors, "LAST_RUN_MISSING", repr(state.get("last_run")))
    else:
        expected_run_id = last_run.stem
        if state.get("updated_by_run") != expected_run_id:
            _error(
                errors,
                "UPDATED_BY_RUN_MISMATCH",
                f"expected {expected_run_id!r}, got {state.get('updated_by_run')!r}",
            )
        if isinstance(last_completed, str):
            completed_by = tasks.get(last_completed, {}).get("completed_by_run")
            completed_path = _run_record_path(root, completed_by)
            if completed_path is None or completed_path.resolve() != last_run.resolve():
                _error(
                    errors,
                    "LAST_COMPLETED_RUN_MISMATCH",
                    f"{last_completed}: {completed_by!r}",
                )

    candidates = ready_tasks(tasks, state)
    recommended = state.get("recommended_next_task")
    if candidates:
        if recommended not in tasks:
            _error(errors, "RECOMMENDATION_UNKNOWN", repr(recommended))
        elif tasks[recommended].get("status") != "READY":
            _error(errors, "RECOMMENDATION_NOT_READY", repr(recommended))
        elif recommended in blocked_ids or not _prerequisites_done(tasks[recommended], tasks):
            _error(errors, "RECOMMENDATION_INELIGIBLE", repr(recommended))
        if recommended != candidates[0]:
            _error(
                errors,
                "RECOMMENDATION_MISMATCH",
                f"expected {candidates[0]!r}, got {recommended!r}",
            )
    elif recommended is not None:
        _error(
            errors,
            "RECOMMENDATION_WITHOUT_READY_TASK",
            repr(recommended),
        )

    next_task_path = root / "CODEX_NEXT_TASK.md"
    try:
        next_task_text = next_task_path.read_text(encoding="utf-8")
    except OSError:
        _error(errors, "NEXT_TASK_STALE", "CODEX_NEXT_TASK.md missing or unreadable")
    else:
        if recommended is not None and str(recommended) not in next_task_text:
            _error(errors, "NEXT_TASK_STALE", f"missing recommended task {recommended}")
        if recommended is None and "NO_READY_TASK" not in next_task_text:
            _error(errors, "NEXT_TASK_STALE", "missing NO_READY_TASK")

    for relative in SNAPSHOT_PATHS:
        snapshot = _load_yaml(root / relative, errors, relative)
        if not isinstance(snapshot, dict):
            continue
        for field in ("generated_by_run", "updated_by_run"):
            run_id = snapshot.get(field)
            run_path = _run_record_path(root, run_id)
            if not isinstance(run_id, str) or not run_id.strip() or run_path is None or not run_path.is_file():
                _error(errors, "SNAPSHOT_PROVENANCE_RUN_MISSING", f"{relative}.{field}={run_id!r}")
        commit = snapshot.get("evidence_as_of_commit")
        if COMMIT_RE.fullmatch(str(commit or "")) is None:
            _error(errors, "SNAPSHOT_PROVENANCE_COMMIT_INVALID", f"{relative}: {commit!r}")

    try:
        state_text = state_path.read_text(encoding="utf-8")
    except OSError as exc:  # pragma: no cover - already caught during YAML load
        _error(errors, "STATE_READ_FAILED", str(exc))
    else:
        for marker in sorted(FOREIGN_PROJECT_MARKERS):
            if marker in state_text:
                _error(errors, "FOREIGN_PROJECT_STATE", marker)

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="project root; defaults to the parent of scripts/",
    )
    args = parser.parse_args(argv)
    root = args.root.resolve()
    errors = validate(root)
    if errors:
        print("PROJECT STATE INVALID")
        for item in errors:
            print(item)
        return 1
    tasks = _load_yaml(root / "TASKS.yaml", [], "TASKS.yaml")
    done = sum(
        isinstance(task, dict) and task.get("status") == "DONE"
        for task in tasks.values()
    )
    print(f"PROJECT STATE VALID | tasks={len(tasks)} | done={done}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
