"""Tests for Markdown generation."""

import os

from mdharness.generator import (
    generate_adr_markdown,
    generate_rule_markdown,
    generate_rules_file_markdown,
    write_adr_files,
    write_rules_files,
)


class TestGenerateAdrMarkdown:
    def test_basic_output(self):
        record = {
            "id": "0001",
            "code": "use-postgres",
            "title": "Use PostgreSQL",
            "status": "Accepted",
            "date": "2024-01-15",
            "decider": "Team",
            "rules-concerned": ["DATA-0001", "SEC-0001"],
            "applied-to": {
                "languages": ["ALL"],
                "frameworks": ["ALL"],
                "types": ["api", "worker"],
            },
            "context": "We need a database.",
            "decision": "Use PostgreSQL.",
            "consequences": "Teams must adopt it.",
        }
        md = generate_adr_markdown(record)
        assert "# 0001. Use PostgreSQL" in md
        assert "status: Accepted" in md
        assert "date: 2024-01-15" in md
        assert "decider: Team" in md
        assert "rules-concerned: [DATA-0001, SEC-0001]" in md
        assert "applied-to" not in md
        assert "## Context" in md
        assert "## Decision" in md
        assert "## Consequences" in md

    def test_empty_rules_concerned(self):
        record = {
            "id": "0001", "code": "test", "title": "T",
            "status": "Accepted", "date": "2024-01-01", "decider": "X",
            "rules-concerned": [],
            "applied-to": {"languages": ["ALL"], "frameworks": ["ALL"], "types": ["ALL"]},
            "context": "C", "decision": "D", "consequences": "Co",
        }
        md = generate_adr_markdown(record)
        assert "rules-concerned: []" in md


class TestGenerateRuleMarkdown:
    def test_basic_output(self):
        rule = {
            "id": "SEC-0001",
            "title": "Validate input",
            "level": "MUST",
            "owner": "Security Team",
            "applied-to": {
                "languages": ["ALL"],
                "frameworks": ["ALL"],
                "types": ["ALL"],
            },
            "waivable": False,
            "since": "0.1.0",
            "description": "All input must be validated.",
            "content": "Validate at boundary.",
        }
        md = generate_rule_markdown(rule)
        assert "## SEC-0001. Validate input" in md
        assert "level: MUST" in md
        assert "owner: Security Team" in md
        assert "applied-to" not in md
        assert "waivable: false" in md
        assert "since: 0.1.0" in md
        assert "All input must be validated." in md
        assert "Validate at boundary." in md

    def test_waivable_defaults_to_true(self):
        rule = {
            "id": "SEC-0001", "title": "T", "level": "MUST", "owner": "O",
            "applied-to": {"languages": ["ALL"], "frameworks": ["ALL"], "types": ["ALL"]},
            "since": "0.1.0", "description": "D", "content": "C",
        }
        md = generate_rule_markdown(rule)
        assert "waivable: true" in md


class TestGenerateRulesFileMarkdown:
    def test_heading_uses_category_name(self):
        rules = [{
            "id": "SEC-0001", "title": "T", "level": "MUST", "owner": "O",
            "applied-to": {"languages": ["ALL"], "frameworks": ["ALL"], "types": ["ALL"]},
            "since": "0.1.0", "description": "D", "content": "C",
        }]
        md = generate_rules_file_markdown("security", rules)
        assert "# Rules of Security" in md

    def test_multiple_rules_in_order(self):
        rules = [
            {"id": "SEC-0001", "title": "First", "level": "MUST", "owner": "O",
             "applied-to": {"languages": ["ALL"], "frameworks": ["ALL"], "types": ["ALL"]},
             "since": "0.1.0", "description": "D1", "content": "C1"},
            {"id": "SEC-0002", "title": "Second", "level": "SHOULD", "owner": "O",
             "applied-to": {"languages": ["ALL"], "frameworks": ["ALL"], "types": ["ALL"]},
             "since": "0.1.0", "description": "D2", "content": "C2"},
        ]
        md = generate_rules_file_markdown("security", rules)
        first_pos = md.index("SEC-0001")
        second_pos = md.index("SEC-0002")
        assert first_pos < second_pos


class TestWriteFiles:
    def test_write_adr_files(self, tmp_path):
        records = [{
            "id": "0001", "code": "use-postgres", "title": "Use PostgreSQL",
            "status": "Accepted", "date": "2024-01-15", "decider": "Team",
            "rules-concerned": [],
            "applied-to": {"languages": ["ALL"], "frameworks": ["ALL"], "types": ["ALL"]},
            "context": "C", "decision": "D", "consequences": "Co",
        }]
        target = str(tmp_path / "target")
        written = write_adr_files(records, target)
        assert len(written) == 1
        assert "adr-0001-use-postgres.md" in written
        assert os.path.exists(os.path.join(target, "adr", "adr-0001-use-postgres.md"))

    def test_write_rules_files(self, tmp_path):
        filtered = {
            "security": [{
                "id": "SEC-0001", "title": "T", "level": "MUST", "owner": "O",
                "applied-to": {"languages": ["ALL"], "frameworks": ["ALL"], "types": ["ALL"]},
                "since": "0.1.0", "description": "D", "content": "C",
            }],
            "testing": [],
        }
        target = str(tmp_path / "target")
        written = write_rules_files(filtered, target)
        assert "security.md" in written
        assert "testing.md" not in written  # empty category skipped
        assert os.path.exists(os.path.join(target, "rules", "security.md"))
