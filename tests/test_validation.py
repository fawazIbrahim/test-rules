"""Tests for validation logic."""

import pytest

from mdharness.validation import validate_adrs, validate_rules, collect_all_rule_ids


class TestAdrValidation:
    def test_valid_adr_passes(self):
        records = [{
            "id": "0001",
            "code": "use-postgres",
            "title": "Use PostgreSQL",
            "status": "Accepted",
            "date": "2024-01-15",
            "decider": "Team",
            "rules-concerned": [],
            "applied-to": {
                "languages": ["ALL"],
                "frameworks": ["ALL"],
                "types": ["ALL"],
            },
            "context": "Context.",
            "decision": "Decision.",
            "consequences": "Consequences.",
        }]
        errors, warnings = validate_adrs(records)
        assert len(errors) == 0

    def test_duplicate_adr_id(self):
        base = {
            "code": "a", "title": "T", "status": "Accepted", "date": "2024-01-01",
            "decider": "X", "rules-concerned": [],
            "applied-to": {"languages": ["ALL"], "frameworks": ["ALL"], "types": ["ALL"]},
            "context": "C", "decision": "D", "consequences": "Co",
        }
        records = [
            {**base, "id": "0001", "code": "first"},
            {**base, "id": "0001", "code": "second"},
        ]
        errors, _ = validate_adrs(records)
        assert any("duplicate ADR id" in e for e in errors)

    def test_duplicate_adr_code(self):
        base = {
            "title": "T", "status": "Accepted", "date": "2024-01-01",
            "decider": "X", "rules-concerned": [],
            "applied-to": {"languages": ["ALL"], "frameworks": ["ALL"], "types": ["ALL"]},
            "context": "C", "decision": "D", "consequences": "Co",
        }
        records = [
            {**base, "id": "0001", "code": "same-code"},
            {**base, "id": "0002", "code": "same-code"},
        ]
        errors, _ = validate_adrs(records)
        assert any("duplicate ADR code" in e for e in errors)

    def test_invalid_id_format(self):
        records = [{
            "id": "1",
            "code": "test", "title": "T", "status": "Accepted", "date": "2024-01-01",
            "decider": "X", "rules-concerned": [],
            "applied-to": {"languages": ["ALL"], "frameworks": ["ALL"], "types": ["ALL"]},
            "context": "C", "decision": "D", "consequences": "Co",
        }]
        errors, _ = validate_adrs(records)
        assert any("zero-padded 4-digit" in e for e in errors)

    def test_invalid_code_format(self):
        records = [{
            "id": "0001",
            "code": "Has Spaces",
            "title": "T", "status": "Accepted", "date": "2024-01-01",
            "decider": "X", "rules-concerned": [],
            "applied-to": {"languages": ["ALL"], "frameworks": ["ALL"], "types": ["ALL"]},
            "context": "C", "decision": "D", "consequences": "Co",
        }]
        errors, _ = validate_adrs(records)
        assert any("lowercase alphanumeric" in e for e in errors)

    def test_invalid_date_format(self):
        records = [{
            "id": "0001", "code": "test", "title": "T", "status": "Accepted",
            "date": "Jan 15 2024",
            "decider": "X", "rules-concerned": [],
            "applied-to": {"languages": ["ALL"], "frameworks": ["ALL"], "types": ["ALL"]},
            "context": "C", "decision": "D", "consequences": "Co",
        }]
        errors, _ = validate_adrs(records)
        assert any("YYYY-MM-DD" in e for e in errors)

    def test_invalid_status(self):
        records = [{
            "id": "0001", "code": "test", "title": "T",
            "status": "Draft",
            "date": "2024-01-01",
            "decider": "X", "rules-concerned": [],
            "applied-to": {"languages": ["ALL"], "frameworks": ["ALL"], "types": ["ALL"]},
            "context": "C", "decision": "D", "consequences": "Co",
        }]
        errors, _ = validate_adrs(records)
        assert any("invalid status" in e for e in errors)

    def test_missing_required_field(self):
        records = [{"id": "0001"}]
        errors, _ = validate_adrs(records)
        assert any("missing required field" in e for e in errors)

    def test_rules_concerned_warns_on_unknown(self):
        records = [{
            "id": "0001", "code": "test", "title": "T", "status": "Accepted",
            "date": "2024-01-01", "decider": "X",
            "rules-concerned": ["UNKNOWN-9999"],
            "applied-to": {"languages": ["ALL"], "frameworks": ["ALL"], "types": ["ALL"]},
            "context": "C", "decision": "D", "consequences": "Co",
        }]
        _, warnings = validate_adrs(records, all_rule_ids=set())
        assert any("unknown rule" in w for w in warnings)

    def test_all_with_other_values_in_applied_to(self):
        records = [{
            "id": "0001", "code": "test", "title": "T", "status": "Accepted",
            "date": "2024-01-01", "decider": "X", "rules-concerned": [],
            "applied-to": {
                "languages": ["ALL", "java"],
                "frameworks": ["ALL"],
                "types": ["ALL"],
            },
            "context": "C", "decision": "D", "consequences": "Co",
        }]
        errors, _ = validate_adrs(records)
        assert any("ALL" in e and "cannot appear alongside" in e for e in errors)

    def test_invalid_language_value(self):
        records = [{
            "id": "0001", "code": "test", "title": "T", "status": "Accepted",
            "date": "2024-01-01", "decider": "X", "rules-concerned": [],
            "applied-to": {
                "languages": ["ruby"],
                "frameworks": ["ALL"],
                "types": ["ALL"],
            },
            "context": "C", "decision": "D", "consequences": "Co",
        }]
        errors, _ = validate_adrs(records)
        assert any("invalid languages value 'ruby'" in e for e in errors)


class TestRulesValidation:
    def test_valid_rule_passes(self):
        all_rules = {
            "security": [{
                "id": "SEC-0001", "title": "T", "level": "MUST", "owner": "Team",
                "applied-to": {"languages": ["ALL"], "frameworks": ["ALL"], "types": ["ALL"]},
                "since": "0.1.0", "description": "D", "content": "C",
            }]
        }
        errors, _ = validate_rules(all_rules)
        assert len(errors) == 0

    def test_duplicate_rule_id(self):
        all_rules = {
            "security": [
                {"id": "SEC-0001", "title": "A", "level": "MUST", "owner": "T",
                 "applied-to": {"languages": ["ALL"], "frameworks": ["ALL"], "types": ["ALL"]},
                 "since": "0.1.0", "description": "D", "content": "C"},
                {"id": "SEC-0001", "title": "B", "level": "MUST", "owner": "T",
                 "applied-to": {"languages": ["ALL"], "frameworks": ["ALL"], "types": ["ALL"]},
                 "since": "0.1.0", "description": "D", "content": "C"},
            ]
        }
        errors, _ = validate_rules(all_rules)
        assert any("duplicate rule id" in e for e in errors)

    def test_prefix_mismatch(self):
        all_rules = {
            "security": [{
                "id": "TEST-0001", "title": "T", "level": "MUST", "owner": "Team",
                "applied-to": {"languages": ["ALL"], "frameworks": ["ALL"], "types": ["ALL"]},
                "since": "0.1.0", "description": "D", "content": "C",
            }]
        }
        errors, _ = validate_rules(all_rules)
        assert any("does not match" in e for e in errors)

    def test_invalid_level(self):
        all_rules = {
            "security": [{
                "id": "SEC-0001", "title": "T", "level": "OPTIONAL", "owner": "Team",
                "applied-to": {"languages": ["ALL"], "frameworks": ["ALL"], "types": ["ALL"]},
                "since": "0.1.0", "description": "D", "content": "C",
            }]
        }
        errors, _ = validate_rules(all_rules)
        assert any("invalid level" in e for e in errors)

    def test_invalid_id_format(self):
        all_rules = {
            "security": [{
                "id": "SEC001", "title": "T", "level": "MUST", "owner": "Team",
                "applied-to": {"languages": ["ALL"], "frameworks": ["ALL"], "types": ["ALL"]},
                "since": "0.1.0", "description": "D", "content": "C",
            }]
        }
        errors, _ = validate_rules(all_rules)
        assert any("PREFIX" in e or "format" in e for e in errors)

    def test_unknown_category(self):
        all_rules = {
            "unknown-category": [{
                "id": "UNK-0001", "title": "T", "level": "MUST", "owner": "Team",
                "applied-to": {"languages": ["ALL"], "frameworks": ["ALL"], "types": ["ALL"]},
                "since": "0.1.0", "description": "D", "content": "C",
            }]
        }
        errors, _ = validate_rules(all_rules)
        assert any("Unknown category" in e for e in errors)

    def test_missing_required_field(self):
        all_rules = {
            "security": [{"id": "SEC-0001"}]
        }
        errors, _ = validate_rules(all_rules)
        assert any("missing required field" in e for e in errors)

    def test_collect_all_rule_ids(self):
        all_rules = {
            "security": [{"id": "SEC-0001"}, {"id": "SEC-0002"}],
            "testing": [{"id": "TEST-0001"}],
        }
        ids = collect_all_rule_ids(all_rules)
        assert ids == {"SEC-0001", "SEC-0002", "TEST-0001"}
