"""Tests for CLI commands."""

import json
import os

from click.testing import CliRunner

from mdharness.cli import main


class TestGenerate:
    def test_generate_all(self, tmp_source, tmp_target):
        runner = CliRunner()
        result = runner.invoke(main, [
            "--source", tmp_source,
            "--target", tmp_target,
            "generate",
        ])
        assert result.exit_code == 0
        assert "Generated" in result.output
        assert os.path.exists(os.path.join(tmp_target, "adr"))
        assert os.path.exists(os.path.join(tmp_target, "rules"))

    def test_generate_filtered(self, tmp_source, tmp_target):
        runner = CliRunner()
        result = runner.invoke(main, [
            "--source", tmp_source,
            "--target", tmp_target,
            "generate",
            "--languages", "java",
            "--frameworks", "spring",
            "--types", "api",
        ])
        assert result.exit_code == 0
        # SEC-0001 (ALL/ALL/ALL) and SEC-0002 (java+spring/api) should match
        # DATA-0001 (ALL/ALL/api+worker) should match
        # TEST-0001 (ALL/ALL/ALL) should match
        assert os.path.exists(os.path.join(tmp_target, "rules", "security.md"))

    def test_generate_dry_run(self, tmp_source, tmp_target):
        runner = CliRunner()
        result = runner.invoke(main, [
            "--source", tmp_source,
            "--target", tmp_target,
            "generate",
            "--dry-run",
        ])
        assert result.exit_code == 0
        assert "Dry run" in result.output
        assert not os.path.exists(tmp_target)

    def test_generate_clean(self, tmp_source, tmp_target):
        os.makedirs(tmp_target)
        dummy = os.path.join(tmp_target, "old-file.txt")
        with open(dummy, "w") as f:
            f.write("old")

        runner = CliRunner()
        result = runner.invoke(main, [
            "--source", tmp_source,
            "--target", tmp_target,
            "generate",
            "--clean",
        ])
        assert result.exit_code == 0
        assert not os.path.exists(dummy)

    def test_generate_skips_empty_categories(self, tmp_source, tmp_target):
        runner = CliRunner()
        result = runner.invoke(main, [
            "--source", tmp_source,
            "--target", tmp_target,
            "generate",
            "--languages", "go",
            "--frameworks", "ALL",
            "--types", "cli",
        ])
        assert result.exit_code == 0
        # SEC-0002 is java+python/spring+fastapi/api — should NOT match go/cli
        # SEC-0001, TEST-0001, DATA-0001 are ALL — they match anything
        security_path = os.path.join(tmp_target, "rules", "security.md")
        if os.path.exists(security_path):
            with open(security_path, "r") as f:
                content = f.read()
            # SEC-0001 (ALL) should be there, SEC-0002 should not
            assert "SEC-0001" in content


class TestValidate:
    def test_validate_valid_source(self, tmp_source):
        runner = CliRunner()
        result = runner.invoke(main, [
            "--source", tmp_source,
            "validate",
        ])
        assert result.exit_code == 0
        assert "Validation passed" in result.output

    def test_validate_with_errors(self, tmp_path):
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        catalog = source_dir / "rules-catalog"
        catalog.mkdir()

        import yaml
        bad_rules = {"rules": [{"id": "WRONG"}]}
        with open(catalog / "security-rules.yaml", "w") as f:
            yaml.dump(bad_rules, f)

        runner = CliRunner()
        result = runner.invoke(main, [
            "--source", str(source_dir),
            "validate",
        ])
        assert result.exit_code == 1
        assert "ERROR" in result.output


class TestRulesSearch:
    def test_search_all(self, tmp_source):
        runner = CliRunner()
        result = runner.invoke(main, [
            "--source", tmp_source,
            "rules", "search",
        ])
        assert result.exit_code == 0
        assert "SEC-0001" in result.output
        assert "SEC-0002" in result.output
        assert "TEST-0001" in result.output

    def test_search_by_level(self, tmp_source):
        runner = CliRunner()
        result = runner.invoke(main, [
            "--source", tmp_source,
            "rules", "search",
            "--level", "SHOULD",
        ])
        assert result.exit_code == 0
        assert "TEST-0001" in result.output
        assert "SEC-0001" not in result.output

    def test_search_by_category(self, tmp_source):
        runner = CliRunner()
        result = runner.invoke(main, [
            "--source", tmp_source,
            "rules", "search",
            "--category", "security",
        ])
        assert result.exit_code == 0
        assert "SEC-0001" in result.output
        assert "TEST-0001" not in result.output

    def test_search_by_title(self, tmp_source):
        runner = CliRunner()
        result = runner.invoke(main, [
            "--source", tmp_source,
            "rules", "search",
            "--title", "parameterized",
        ])
        assert result.exit_code == 0
        assert "SEC-0002" in result.output
        assert "SEC-0001" not in result.output

    def test_search_by_id_prefix(self, tmp_source):
        runner = CliRunner()
        result = runner.invoke(main, [
            "--source", tmp_source,
            "rules", "search",
            "--id", "SEC",
        ])
        assert result.exit_code == 0
        assert "SEC-0001" in result.output
        assert "TEST-0001" not in result.output

    def test_search_format_json(self, tmp_source):
        runner = CliRunner()
        result = runner.invoke(main, [
            "--source", tmp_source,
            "rules", "search",
            "--format", "json",
        ])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert len(data) > 0

    def test_search_format_ids(self, tmp_source):
        runner = CliRunner()
        result = runner.invoke(main, [
            "--source", tmp_source,
            "rules", "search",
            "--format", "ids",
        ])
        assert result.exit_code == 0
        lines = result.output.strip().split("\n")
        assert "SEC-0001" in lines

    def test_search_waivable_false(self, tmp_source):
        runner = CliRunner()
        result = runner.invoke(main, [
            "--source", tmp_source,
            "rules", "search",
            "--waivable", "false",
        ])
        assert result.exit_code == 0
        assert "SEC-0001" in result.output
        assert "SEC-0002" not in result.output  # defaults to true

    def test_search_by_owner(self, tmp_source):
        runner = CliRunner()
        result = runner.invoke(main, [
            "--source", tmp_source,
            "rules", "search",
            "--owner", "QA",
        ])
        assert result.exit_code == 0
        assert "TEST-0001" in result.output
        assert "SEC-0001" not in result.output


class TestRulesCount:
    def test_count_all(self, tmp_source):
        runner = CliRunner()
        result = runner.invoke(main, [
            "--source", tmp_source,
            "rules", "count",
        ])
        assert result.exit_code == 0
        assert "Total: 4" in result.output

    def test_count_group_by_category(self, tmp_source):
        runner = CliRunner()
        result = runner.invoke(main, [
            "--source", tmp_source,
            "rules", "count",
            "--group-by", "category",
        ])
        assert result.exit_code == 0
        assert "security" in result.output
        assert "testing" in result.output

    def test_count_with_level_filter(self, tmp_source):
        runner = CliRunner()
        result = runner.invoke(main, [
            "--source", tmp_source,
            "rules", "count",
            "--level", "MUST",
        ])
        assert result.exit_code == 0
        assert "Total: 3" in result.output  # SEC-0001, SEC-0002, DATA-0001


class TestRulesShow:
    def test_show_existing_rule(self, tmp_source):
        runner = CliRunner()
        result = runner.invoke(main, [
            "--source", tmp_source,
            "rules", "show", "SEC-0001",
        ])
        assert result.exit_code == 0
        assert "SEC-0001" in result.output
        assert "Validate all user input" in result.output

    def test_show_nonexistent_rule(self, tmp_source):
        runner = CliRunner()
        result = runner.invoke(main, [
            "--source", tmp_source,
            "rules", "show", "NOPE-9999",
        ])
        assert result.exit_code == 2


class TestAdrList:
    def test_list_all(self, tmp_source):
        runner = CliRunner()
        result = runner.invoke(main, [
            "--source", tmp_source,
            "adr", "list",
        ])
        assert result.exit_code == 0
        assert "0001" in result.output
        assert "0002" in result.output

    def test_list_filter_by_status(self, tmp_source):
        runner = CliRunner()
        result = runner.invoke(main, [
            "--source", tmp_source,
            "adr", "list",
            "--status", "Deprecated",
        ])
        assert result.exit_code == 0
        assert "0001" not in result.output

    def test_list_format_json(self, tmp_source):
        runner = CliRunner()
        result = runner.invoke(main, [
            "--source", tmp_source,
            "adr", "list",
            "--format", "json",
        ])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert len(data) == 2


class TestAdrShow:
    def test_show_existing_adr(self, tmp_source):
        runner = CliRunner()
        result = runner.invoke(main, [
            "--source", tmp_source,
            "adr", "show", "0001",
        ])
        assert result.exit_code == 0
        assert "0001" in result.output
        assert "Use PostgreSQL" in result.output

    def test_show_nonexistent_adr(self, tmp_source):
        runner = CliRunner()
        result = runner.invoke(main, [
            "--source", tmp_source,
            "adr", "show", "9999",
        ])
        assert result.exit_code == 2


class TestVersion:
    def test_version_flag(self):
        runner = CliRunner()
        result = runner.invoke(main, ["--version"])
        assert result.exit_code == 0
        assert "0.1.0" in result.output
