"""Tests for YAML loading."""

import os
import yaml

from mdharness.loader import load_adr_file, load_rules_file, load_all_rules


class TestLoadAdrFile:
    def test_load_valid_adr(self, tmp_path):
        source = tmp_path / "source"
        source.mkdir()
        data = {"records": [{"id": "0001", "title": "Test"}]}
        with open(source / "adr.yaml", "w") as f:
            yaml.dump(data, f)
        result = load_adr_file(str(source))
        assert len(result) == 1
        assert result[0]["id"] == "0001"

    def test_missing_adr_file(self, tmp_path):
        result = load_adr_file(str(tmp_path))
        assert result == []

    def test_empty_adr_file(self, tmp_path):
        source = tmp_path / "source"
        source.mkdir()
        with open(source / "adr.yaml", "w") as f:
            f.write("")
        result = load_adr_file(str(source))
        assert result == []


class TestLoadRulesFile:
    def test_load_valid_rules(self, tmp_path):
        data = {"rules": [{"id": "SEC-0001"}, {"id": "SEC-0002"}]}
        path = tmp_path / "security-rules.yaml"
        with open(path, "w") as f:
            yaml.dump(data, f)
        result = load_rules_file(str(path))
        assert len(result) == 2

    def test_empty_rules_file(self, tmp_path):
        path = tmp_path / "empty-rules.yaml"
        with open(path, "w") as f:
            f.write("")
        result = load_rules_file(str(path))
        assert result == []


class TestLoadAllRules:
    def test_load_multiple_files(self, tmp_path):
        source = tmp_path / "source"
        catalog = source / "rules-catalog"
        catalog.mkdir(parents=True)

        for name, rules in [
            ("security-rules.yaml", [{"id": "SEC-0001"}]),
            ("testing-rules.yaml", [{"id": "TEST-0001"}, {"id": "TEST-0002"}]),
        ]:
            with open(catalog / name, "w") as f:
                yaml.dump({"rules": rules}, f)

        result = load_all_rules(str(source))
        assert "security" in result
        assert "testing" in result
        assert len(result["security"]) == 1
        assert len(result["testing"]) == 2

    def test_missing_catalog_dir(self, tmp_path):
        result = load_all_rules(str(tmp_path))
        assert result == {}

    def test_ignores_non_rules_files(self, tmp_path):
        source = tmp_path / "source"
        catalog = source / "rules-catalog"
        catalog.mkdir(parents=True)

        with open(catalog / "readme.md", "w") as f:
            f.write("Not a rules file")
        with open(catalog / "security-rules.yaml", "w") as f:
            yaml.dump({"rules": [{"id": "SEC-0001"}]}, f)

        result = load_all_rules(str(source))
        assert len(result) == 1
        assert "security" in result
