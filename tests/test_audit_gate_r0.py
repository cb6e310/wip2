from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import inspect
import os
import shutil
import subprocess
import sys
import tempfile
import types
import unittest
import warnings
from collections import Counter, defaultdict
from pathlib import Path
from unittest import mock

import numpy as np
import torch
from sklearn.exceptions import ConvergenceWarning


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/audit_gate_r0.py"


def _import(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


gate = _import("audit_gate_r0", SCRIPT)


def _oracle(rows: list[dict]) -> tuple[list[dict], list[dict], bytes, bytes]:
    subjects = sorted({row["subject"] for row in rows})
    lengths = ("W01_04", "W05_16", "W17_PLUS")
    powers = ("P_LOW", "P_HIGH")
    roles = ("train_fit", "inner_val")
    eligible = [
        row for row in rows
        if row["a_interface_status"] == "ELIGIBLE"
        and row["action"] == "RUN_FRONTEND"
        and row["power_edge_status"] == "PASS"
    ]
    grouped = defaultdict(list)
    for row in eligible:
        grouped[(row["subject"], row["length_bin"], row["power_bin"], row["role"])].append(row)
    support = []
    panel = []
    for subject in subjects:
        for length_bin in lengths:
            for power_bin in powers:
                candidates = {role: grouped[(subject, length_bin, power_bin, role)] for role in roles}
                train_n = len(candidates["train_fit"])
                inner_n = len(candidates["inner_val"])
                status = (
                    "MATCHED_SUPPORT" if train_n and inner_n else
                    "TRAIN_ONLY" if train_n else
                    "INNER_ONLY" if inner_n else "ABSENT_BOTH"
                )
                support.append({
                    "subject": subject, "length_bin": length_bin, "power_bin": power_bin,
                    "train_fit_n": train_n, "inner_val_n": inner_n, "support_status": status,
                })
                if status != "MATCHED_SUPPORT":
                    continue
                for role in roles:
                    ranked = []
                    for row in candidates[role]:
                        canonical = {key: row[key] for key in (
                            "subject", "role", "length_bin", "power_bin", "slot", "occurrence_id"
                        )}
                        encoded = json.dumps(
                            canonical, sort_keys=True, separators=(",", ":"), ensure_ascii=False
                        ).encode("utf-8")
                        digest = hashlib.sha256(b"RC_HSG_GATE_R0_MATCHED_PANEL_V1\0" + encoded).hexdigest()
                        ranked.append((digest, row["slot"], row["occurrence_id"], row))
                    digest, _, _, row = min(ranked)
                    panel.append({
                        "subject": row["subject"], "session": row["session"], "role": row["role"],
                        "length_bin": row["length_bin"], "power_bin": row["power_bin"],
                        "slot": row["slot"], "occurrence_id": row["occurrence_id"],
                        "raw_samples": row["raw_samples"], "window_count": row["window_count"],
                        "source_file": row["source_file"], "source_field": row["source_field"],
                        "selection_sha256": digest,
                    })
    panel.sort(key=lambda row: (
        row["subject"], lengths.index(row["length_bin"]), powers.index(row["power_bin"]),
        roles.index(row["role"]), row["slot"], row["occurrence_id"],
    ))
    render = lambda values: b"".join(
        (json.dumps(value, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")
        for value in values
    )
    return support, panel, render(support), render(panel)


def _passing_gate() -> dict:
    numerical = {
        str(replicate): {
            label: {"all_rows_pass": True}
            for label in (
                "psd_relative_norm", "covariance_relative_norm", "mean_relative_norm",
                "cross_spectrum_relative_norm",
            )
        }
        for replicate in gate.REPLICATES
    }
    classifier = {
        str(replicate): {"point_pass": True, "upper_pass": True}
        for replicate in gate.REPLICATES
    }
    nuisance = {
        label: {"pass": {str(replicate): True for replicate in gate.REPLICATES}}
        for label in ("subject", "length", "power")
    }
    nuisance["session"] = {"real_surrogate_exact_parity": True}
    amplitude = {
        subject: {str(replicate): {"pass": True} for replicate in gate.REPLICATES}
        for subject in gate.SUBJECTS
    }
    return {
        "coverage": {"eligible_all_replicates": True, "no_power_bin_full_audit_rows": 4, "no_power_bin_panel_rows": 0},
        "numerical": numerical, "classifier": classifier, "nuisance": nuisance,
        "amplitude_endpoint": amplitude,
    }


class GateR0Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.paths, _ = gate._verify_inputs(ROOT, True)
        cls.metadata = gate._metadata_preflight(cls.paths, True)
        cls.assignment = gate._load_jsonl(cls.paths["n1_assignment"], "assignment")
        cls.oracle = _oracle(cls.assignment)

    def test_fixed_metadata_counts_and_two_independent_digests(self) -> None:
        actual = self.metadata["actual"]
        for label, expected in gate.EXPECTED.items():
            self.assertEqual(actual[label], expected, label)
        support, panel, support_bytes, panel_bytes = self.oracle
        self.assertEqual(support_bytes, self.metadata["support_bytes"])
        self.assertEqual(panel_bytes, self.metadata["panel_bytes"])
        self.assertEqual(hashlib.sha256(support_bytes).hexdigest(), gate.SUPPORT_SHA256)
        self.assertEqual(hashlib.sha256(panel_bytes).hexdigest(), gate.PANEL_SHA256)
        self.assertEqual(Counter(row["support_status"] for row in support), {
            "MATCHED_SUPPORT": 88, "TRAIN_ONLY": 16, "ABSENT_BOTH": 4,
        })
        self.assertEqual(len(panel), 176)

    def test_support_and_panel_schema_order_role_subject_counts(self) -> None:
        support, panel, _, _ = self.oracle
        self.assertTrue(all(list(row) == [
            "subject", "length_bin", "power_bin", "train_fit_n", "inner_val_n", "support_status"
        ] for row in support))
        self.assertTrue(all(list(row) == [
            "subject", "session", "role", "length_bin", "power_bin", "slot", "occurrence_id",
            "raw_samples", "window_count", "source_file", "source_field", "selection_sha256",
        ] for row in panel))
        self.assertEqual(Counter(row["role"] for row in panel), {"train_fit": 88, "inner_val": 88})
        self.assertEqual(len({row["subject"] for row in panel}), 18)
        self.assertEqual(dict(Counter(row["subject"] for row in panel)), {
            "YAC": 10, "YAG": 12, "YAK": 8, "YDG": 10, "YDR": 10, "YFR": 10,
            "YFS": 10, "YHS": 8, "YIS": 10, "YLS": 12, "YMD": 6, "YMS": 12,
            "YRH": 10, "YRK": 10, "YRP": 10, "YSD": 10, "YSL": 10, "YTL": 8,
        })

    def test_192_role_cell_union_is_not_the_panel(self) -> None:
        passed = [row for row in self.assignment if row.get("power_edge_status") == "PASS"]
        role_cells = defaultdict(list)
        for row in passed:
            role_cells[(row["subject"], row["role"], row["length_bin"], row["power_bin"])].append(row)
        union = [min(rows, key=lambda row: (row["slot"], row["occurrence_id"])) for rows in role_cells.values()]
        self.assertEqual(len(union), 192)
        self.assertNotEqual({_key(row) for row in union}, {_key(row) for row in self.metadata["panel_rows"]})

    def test_borrow_duplicate_replacement_mutations_change_panel_digest(self) -> None:
        _, panel, _, panel_bytes = self.oracle
        mutations = []
        mutations.append(panel + [dict(panel[0])])
        borrowed = [dict(row) for row in panel]
        borrowed[0]["subject"] = borrowed[-1]["subject"]
        mutations.append(borrowed)
        replaced = [dict(row) for row in panel]
        replaced[0] = dict(replaced[2])
        mutations.append(replaced)
        for mutation in mutations:
            rendered = b"".join(
                (json.dumps(row, separators=(",", ":"), ensure_ascii=False) + "\n").encode()
                for row in mutation
            )
            self.assertNotEqual(rendered, panel_bytes)
            self.assertNotEqual(hashlib.sha256(rendered).hexdigest(), gate.PANEL_SHA256)

    def test_missing_role_and_altered_power_status_fail_panel_contract(self) -> None:
        rows = [dict(row) for row in self.metadata["eligible"]]
        target = next(row for row in self.metadata["support_rows"] if row["support_status"] == "MATCHED_SUPPORT")
        for fault in ("missing-role", "altered-power"):
            mutated = [dict(row) for row in rows]
            candidates = [row for row in mutated if (
                row["subject"], row["length_bin"], row["power_bin"], row["role"]
            ) == (target["subject"], target["length_bin"], target["power_bin"], "inner_val")]
            if fault == "missing-role":
                mutated = [row for row in mutated if row not in candidates]
            else:
                for row in candidates:
                    row["power_edge_status"] = "INSUFFICIENT_TRAIN_CELL"
                    row["power_bin"] = None
            with self.assertRaisesRegex(gate.GateR0TechnicalAbort, "panel-subject-counts"):
                gate._build_support_panel(mutated)

    def test_four_no_bin_rows_are_full_only(self) -> None:
        rows = [row for row in self.metadata["eligible"] if row["power_edge_status"] != "PASS"]
        self.assertEqual([(r["subject"], r["role"], r["slot"]) for r in rows], [
            ("YAK", "train_fit", 307), ("YAK", "inner_val", 323),
            ("YHS", "train_fit", 11), ("YHS", "train_fit", 16),
        ])
        self.assertTrue({_key(row) for row in rows}.isdisjoint(self.metadata["panel_keys"]))

    def test_bootstrap_hash_shape_and_order_statistic(self) -> None:
        indices = gate._bootstrap_indices()
        self.assertEqual(indices.shape, (10_000, 18))
        self.assertEqual(hashlib.sha256(indices.tobytes()).hexdigest(), gate.BOOTSTRAP_SHA256)
        values = np.arange(18, dtype=np.float64) / 17.0
        upper = float(np.sort(values[indices].mean(axis=1))[9749])
        self.assertTrue(0.0 <= upper <= 1.0)

    def test_n1_metadata_replay_has_no_reader_dependency(self) -> None:
        with mock.patch.object(gate, "_load_reader", side_effect=AssertionError("no reader")):
            result = gate._n1_audit(ROOT)
        self.assertEqual(result["structural_integrity"], "PASS")
        self.assertEqual(result["primary_fallback"], "INELIGIBLE_DEGRADED_COVERAGE")
        self.assertEqual(result["new_real_eeg_reads"], 0)
        self.assertEqual(result["fixed_points_total"], 35529)

    def test_feature_vector_uses_exact_tokenizer_shape_and_order(self) -> None:
        reader = gate._load_reader(self.paths["reader"])
        tokenizer = gate._TokenizerOnly()
        time = torch.arange(500, dtype=torch.float32) / 500.0
        values = torch.stack([torch.sin((index + 1) * time) for index in range(105)]).contiguous()
        vector = gate._audit_vector(reader, tokenizer, values, 1)
        self.assertEqual(vector.shape, (2429,))
        with torch.inference_mode():
            tokens = reader.NativeSpectralA1._spectral_tokens(tokenizer, values, 500).numpy().astype(np.float64)
        np.testing.assert_array_equal(vector[:840], tokens.mean(axis=0))
        np.testing.assert_array_equal(vector[840:1680], tokens.std(axis=0, ddof=0))
        with self.assertRaisesRegex(gate.GateR0TechnicalAbort, "tokens"):
            gate._audit_vector(reader, tokenizer, values, 2)

    def test_numerical_and_amplitude_metrics_are_finite(self) -> None:
        samples = 513
        time = torch.arange(samples, dtype=torch.float32) / samples
        values = torch.stack([torch.sin((index % 7 + 1) * 6.0 * time) for index in range(105)]).contiguous()
        surrogate = gate.N2CommonPhaseSampler().generate_unpadded(values, "SYN\t000001\tgate", 1).values
        numerical = gate._numerical_metrics(values, surrogate)
        self.assertTrue(all(np.isfinite(value) and value <= 1.0e-6 for value in numerical.values()))
        amplitude = gate._amplitude_metrics(values, surrogate)
        self.assertTrue(all(np.isfinite(value) for value in amplitude.values()))

    def test_v292_and_v293_model_preflights_are_warning_free_and_exact(self) -> None:
        filters_before = list(warnings.filters)
        certificate, rendered = gate._model_api_preflight()
        second_certificate, second_rendered = gate._model_api_preflight()
        binary = certificate["legacy_modern_binary"]
        self.assertEqual(certificate["sklearn_version"], "1.9.0")
        self.assertEqual(binary["legacy_warning_count"], 1)
        self.assertEqual(binary["legacy_warning_category"], "FutureWarning")
        self.assertEqual(binary["modern_warning_count"], 0)
        self.assertEqual(set(binary["maximum_absolute_difference"].values()), {0.0})
        self.assertEqual([item["K"] for item in certificate["multiclass_capability"]], [2, 3, 18])
        self.assertTrue(all(item["warning_count"] == 0 for item in certificate["multiclass_capability"]))
        self.assertEqual(rendered, gate._yaml_bytes(certificate))
        self.assertEqual(certificate, second_certificate)
        self.assertEqual(rendered, second_rendered)
        self.assertEqual(warnings.filters, filters_before)
        self.assertNotIn(b"fixture", rendered.lower().replace(b"fixture_or_model_values_persisted", b""))
        for forbidden in (b"coefficient_values", b"probability_values", b"decision_values"):
            self.assertNotIn(forbidden, rendered)

    def test_production_constructor_is_the_exact_modern_api(self) -> None:
        source = inspect.getsource(gate._production_model)
        self.assertNotIn("penalty=", source)
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            model = gate._production_model()
        self.assertEqual(caught, [])
        params = model.get_params(deep=False)
        for key, value in gate.MODEL_PARAMETERS.items():
            self.assertEqual(params[key], value)
        with self.assertRaises(TypeError):
            gate._production_model(penalty="l2")

    def test_constructor_parameter_and_warning_mutations_fail_closed(self) -> None:
        x = np.asarray([[-2.0], [-1.0], [1.0], [2.0]])
        y = np.asarray([0, 0, 1, 1], dtype=np.int8)
        mutations = {
            "l1_ratio": 0.5, "C": 2.0, "solver": "liblinear", "tol": 1.0e-4,
            "max_iter": 1999, "fit_intercept": False, "class_weight": "balanced",
            "warm_start": True,
        }
        for key, value in mutations.items():
            parameters = dict(gate.MODEL_PARAMETERS)
            parameters[key] = value
            with mock.patch.object(gate, "_production_model", return_value=gate.LogisticRegression(**parameters)):
                with self.assertRaisesRegex(gate.GateR0TechnicalAbort, "GATE_R0_MODEL_FIT_INVALID"):
                    gate._fit_logistic(x, y, "reference_detector", ("real", "N2"), (x,))
        original = gate._production_model
        for category in (FutureWarning, ConvergenceWarning, RuntimeWarning, UserWarning):
            def warned(category=category):
                warnings.warn("injected", category)
                return original()
            with mock.patch.object(gate, "_production_model", side_effect=warned):
                with self.assertRaisesRegex(gate.GateR0TechnicalAbort, "GATE_R0_MODEL_FIT_INVALID"):
                    gate._fit_logistic(x, y, "reference_detector", ("real", "N2"), (x,))

    def test_api_equivalence_warning_version_and_numerical_mutations_fail_closed(self) -> None:
        with mock.patch("sklearn.__version__", "1.9.1"):
            with self.assertRaisesRegex(gate.GateR0TechnicalAbort, "GATE_R0_MODEL_API_EQUIVALENCE_MISMATCH"):
                gate._model_api_preflight()
        with mock.patch.object(gate, "_normalized_warning_message", return_value="wrong warning"):
            with self.assertRaisesRegex(gate.GateR0TechnicalAbort, "GATE_R0_MODEL_API_EQUIVALENCE_MISMATCH"):
                gate._model_api_preflight()
        with mock.patch.object(gate.np, "allclose", return_value=False):
            with self.assertRaisesRegex(gate.GateR0TechnicalAbort, "GATE_R0_MODEL_API_EQUIVALENCE_MISMATCH"):
                gate._model_api_preflight()

    def test_fit_type_domains_preserve_exact_targets(self) -> None:
        cases = (
            ("reference_detector", ("real", "N2"), np.asarray([0, 1, 0, 1], dtype=np.int8), [0, 1]),
            ("nuisance_subject", gate.SUBJECTS, np.asarray(gate.SUBJECTS), list(gate.SUBJECTS)),
            ("nuisance_length", ("W01_04", "W05_16", "W17_PLUS"), np.asarray(["W01_04", "W05_16", "W17_PLUS"]), ["W01_04", "W05_16", "W17_PLUS"]),
            ("nuisance_power", ("P_LOW", "P_HIGH"), np.asarray(["P_LOW", "P_HIGH"]), ["P_HIGH", "P_LOW"]),
        )
        for fit_type, domain, target, expected in cases:
            classes, cardinality = gate._semantic_classes(fit_type, domain, target)
            self.assertEqual(classes.tolist(), expected)
            self.assertEqual(cardinality, len(expected))

    def test_domain_reencoding_merge_extra_and_unknown_fit_fail_closed(self) -> None:
        failures = (
            ("nuisance_subject", gate.SUBJECTS[:-1], np.asarray(gate.SUBJECTS[:-1])),
            ("nuisance_subject", (*gate.SUBJECTS, "EXTRA"), np.asarray((*gate.SUBJECTS, "EXTRA"))),
            ("nuisance_length", gate.FIT_DOMAINS["nuisance_length"], np.asarray([0, 1, 2])),
            ("nuisance_power", gate.FIT_DOMAINS["nuisance_power"], np.asarray([0, 0])),
            ("unknown", ("a", "b"), np.asarray(["a", "b"])),
        )
        for fit_type, domain, target in failures:
            with self.assertRaisesRegex(gate.GateR0TechnicalAbort, "GATE_R0_MODEL_FIT_INVALID"):
                gate._semantic_classes(fit_type, domain, target)
        with self.assertRaisesRegex(gate.GateR0TechnicalAbort, "target-(encoding|cardinality):nuisance_subject"):
            gate._semantic_classes("nuisance_subject", gate.SUBJECTS, np.asarray([0, 1] * 9))

    def test_post_fit_classes_and_binary_multiclass_shapes_are_strict(self) -> None:
        _, _, diagnostic = gate._fit_logistic(
            np.asarray([[-2.0], [-1.0], [1.0], [2.0]]),
            np.asarray([0, 0, 1, 1], dtype=np.int8),
            "reference_detector", ("real", "N2"), (np.asarray([[-0.5], [0.5]]),),
        )
        self.assertEqual(diagnostic["classes"], [0, 1])
        self.assertEqual(diagnostic["coef_shape"], [1, 1])
        self.assertEqual(diagnostic["decision_shapes"], [[4], [2]])
        capabilities = gate._model_api_preflight()[0]["multiclass_capability"]
        self.assertEqual(capabilities[1]["coef_shape"], [3, 6])
        self.assertEqual(capabilities[1]["decision_shapes"], [[12, 3]])
        self.assertEqual(capabilities[2]["coef_shape"], [18, 6])
        self.assertEqual(capabilities[2]["decision_shapes"], [[72, 18]])

    def test_post_fit_class_iteration_shape_and_finite_mutations_fail_closed(self) -> None:
        x = np.asarray([[-2.0], [-1.0], [1.0], [2.0]])
        y = np.asarray([0, 0, 1, 1], dtype=np.int8)
        expected = np.unique(y)

        def fitted():
            model = gate._production_model()
            model.fit(x, y)
            evaluated = [(x, model.decision_function(x), model.predict_proba(x))]
            return model, evaluated

        for mutation in ("classes", "iterations", "coef", "intercept", "decision", "probability"):
            model, evaluated = fitted()
            if mutation == "classes":
                model.classes_ = model.classes_[::-1]
            elif mutation == "iterations":
                model.n_iter_ = np.asarray([2000])
            elif mutation == "coef":
                model.coef_[0, 0] = np.nan
            elif mutation == "intercept":
                model.intercept_ = np.zeros(2)
            elif mutation == "decision":
                evaluated[0] = (x, np.zeros((len(x), 2)), evaluated[0][2])
            else:
                probability = evaluated[0][2].copy()
                probability[0, 0] = np.nan
                evaluated[0] = (x, evaluated[0][1], probability)
            with self.assertRaisesRegex(gate.GateR0TechnicalAbort, "GATE_R0_MODEL_FIT_INVALID"):
                gate._validate_fitted_model(model, expected, 2, 1, evaluated)

    def test_mechanical_pass_fail_and_inconclusive_branches(self) -> None:
        passing = _passing_gate()
        self.assertEqual(gate._all_pass(passing), ("PASS_N2_PRIMARY_N1_MECHANISM_ONLY", [], []))
        point_fail = _passing_gate()
        point_fail["classifier"]["1"]["point_pass"] = False
        self.assertEqual(gate._all_pass(point_fail)[0], "FAIL_NO_PRIMARY_REFERENCE")
        uncertain = _passing_gate()
        uncertain["classifier"]["2"]["upper_pass"] = False
        decision, failures, inconclusive = gate._all_pass(uncertain)
        self.assertEqual(decision, "FAIL_NO_PRIMARY_REFERENCE")
        self.assertEqual(failures, [])
        self.assertEqual(inconclusive, ["classifier-upper:2"])

    def test_all_frozen_threshold_boundaries_mutate_mechanically(self) -> None:
        self.assertEqual(gate.NUMERICAL_THRESHOLD, 1.0e-6)
        self.assertEqual(gate.CLASSIFIER_THRESHOLD, 0.65)
        self.assertEqual(gate.NUISANCE_THRESHOLD, 0.05)
        self.assertEqual(gate.AMPLITUDE_KS_THRESHOLD, 0.15)
        self.assertEqual(gate.QUANTILE_SHIFT_THRESHOLD, 0.25)
        self.assertEqual((gate.ENDPOINT_RATIO_MIN, gate.ENDPOINT_RATIO_MAX), (0.5, 2.0))
        for path in (
            ("coverage", "eligible_all_replicates"),
            ("nuisance", "power", "pass", "199"),
            ("amplitude_endpoint", "YAC", "1", "pass"),
        ):
            value = _passing_gate()
            target = value
            for key in path[:-1]:
                target = target[key]
            target[path[-1]] = False
            self.assertEqual(gate._all_pass(value)[0], "FAIL_NO_PRIMARY_REFERENCE")

    def test_scan_accounting_separates_full_and_panel_without_persistence(self) -> None:
        rows = []
        for index in range(12):
            rows.append({
                "subject": gate.SUBJECTS[index % 6], "session": 1, "slot": index + 1,
                "occurrence_id": f"o{index:03d}", "role": "inner_val" if index >= 8 else "train_fit",
                "raw_samples": 500, "window_count": 1, "length_bin": "W01_04",
                "power_bin": None if index == 0 else "P_LOW",
                "power_edge_status": "INSUFFICIENT_TRAIN_CELL" if index == 0 else "PASS",
                "source_file": "x", "source_field": "rawData", "source_dataset_read": True,
            })
        panel = [rows[index] for index in (1, 2, 8, 9)]
        metadata = {
            "eligible": rows, "eligible_keys": {gate._key(row) for row in rows},
            "panel_rows": panel, "panel_keys": {gate._key(row) for row in panel},
        }
        reads = []
        class Reader:
            @staticmethod
            def _read_raw(row, dataset, files, keys):
                reads.append(gate._key(row))
                return torch.zeros((1, 105, 500), dtype=torch.float32), "float64"
        class Sampler:
            def generate_unpadded(self, values, row_key, replicate):
                digest = hashlib.sha256(f"{row_key}:{replicate}".encode()).hexdigest()
                return types.SimpleNamespace(values=values, phase_seed_sha256=digest)
        numerical_summary = {
            str(rep): {label: {"count": 12 if rep == 1 else 4, "all_rows_pass": True} for label in (
                "psd_relative_norm", "covariance_relative_norm", "mean_relative_norm", "cross_spectrum_relative_norm"
            )} for rep in gate.REPLICATES
        }
        with (
            mock.patch.object(gate, "N2CommonPhaseSampler", Sampler),
            mock.patch.object(gate, "_audit_vector", return_value=np.zeros(2429)),
            mock.patch.object(gate, "_numerical_metrics", return_value={
                "psd_relative_norm": 0.0, "covariance_relative_norm": 0.0,
                "mean_relative_norm": 0.0, "cross_spectrum_relative_norm": 0.0,
            }),
            mock.patch.object(gate, "_numerical_summary", return_value=numerical_summary),
            mock.patch.object(gate, "_amplitude_metrics", return_value={
                "amplitude_ks": 0.0, "quantile_shift": 0.0, "jump_real": 1.0,
                "jump_surrogate": 1.0, "slip_real": 1.0, "slip_surrogate": 1.0,
            }),
            mock.patch.object(gate, "_amplitude_audit", return_value={}),
        ):
            coverage, scan = gate._scan(Reader, metadata, Path("."), {"x": Path("x")})
        self.assertEqual(reads, [gate._key(row) for row in rows])
        self.assertEqual(len(coverage), 12)
        self.assertEqual(scan["features"][0].shape, (4, 2429))
        self.assertTrue(coverage[0]["no_power_bin_full_only"])
        self.assertFalse(coverage[0]["panel"])

    def test_fixed_hash_tamper_aborts_before_reader_or_output(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary) / "project"
            for relative, _ in {**gate.FIXED_INPUTS, **gate.CONTROL_INPUTS}.values():
                target = project / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(ROOT / relative, target)
            target = project / gate.FIXED_INPUTS["n1_assignment"][0]
            target.write_bytes(target.read_bytes() + b"\n")
            with mock.patch.object(gate, "_load_reader", side_effect=AssertionError("must not import")):
                with self.assertRaisesRegex(gate.GateR0TechnicalAbort, "hash:n1_assignment"):
                    gate.audit_gate_r0(
                        project, Path(temporary) / "dataset", project,
                        (Path(temporary) / "a", Path(temporary) / "b"),
                    )
            self.assertFalse((project / gate.OUTPUTS["gate"]).exists())

    def test_outputs_are_atomic_symlink_safe_and_value_free(self) -> None:
        rendered = {
            "correction": b"scientific_state_changed: false\n",
            "model_certificate": b"verdict: PASS\n",
            "support": self.metadata["support_bytes"], "panel": self.metadata["panel_bytes"],
            "coverage": b'{"row_key":"S\\t000001\\to","read_count":1}\n',
            "gate": b"decision: PASS_N2_PRIMARY_N1_MECHANISM_ONLY\n",
            "report": b"reference integrity only\n",
        }
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "root"
            gate._atomic_write(root, rendered)
            combined = b"".join((root / relative).read_bytes() for relative in gate.OUTPUTS.values()).lower()
            for forbidden in (b"waveform_values", b"surrogate_values", b"token_values", b"feature_values", b"probability_values", b"coefficient_values", b"stimulus_text", b"outcome_values"):
                self.assertNotIn(forbidden, combined)
            if os.name != "nt":
                link = Path(temporary) / "link"
                link.symlink_to(root, target_is_directory=True)
                with self.assertRaisesRegex(gate.GateR0TechnicalAbort, "symlink"):
                    gate._atomic_write(link, rendered)

    def test_cli_rejects_all_scientific_overrides(self) -> None:
        for argument in (
            "--dataset-root", "--role", "--subject", "--row", "--replicate", "--feature",
            "--classifier", "--C", "--threshold", "--resume", "--cache", "--seed", "--hash-override",
        ):
            completed = subprocess.run(
                [
                    sys.executable, str(SCRIPT),
                    "--output-root", str(ROOT),
                    "--verification-root-a", str(ROOT.parent / "verify-a"),
                    "--verification-root-b", str(ROOT.parent / "verify-b"),
                    argument, "x",
                ], cwd=ROOT,
                text=True, capture_output=True, check=False,
            )
            self.assertEqual(completed.returncode, 2, argument)
            self.assertIn("unrecognized arguments", completed.stderr)

    def test_ast_firewall_has_no_direct_hdf5_full_encoder_or_serialization(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8")
        tree = ast.parse(source)
        imports = {
            alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names
        }
        imports |= {node.module or "" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)}
        self.assertNotIn("h5py", imports)
        self.assertNotIn("joblib", imports)
        self.assertNotIn("pickle", imports)
        self.assertNotIn("NativeSpectralA1(", source)
        self.assertNotIn("torch.save", source)
        self.assertNotIn("np.save", source)
        self.assertNotIn("backward(", source)
        self.assertNotIn("optimizer", source.lower())


def _key(row: dict) -> tuple[str, int, str]:
    return row["subject"], row["slot"], row["occurrence_id"]


if __name__ == "__main__":
    unittest.main()
