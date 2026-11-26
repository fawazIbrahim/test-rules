"""Tests for filtering logic."""

from mdharness.filtering import matches_filter, filter_rules, filter_adrs


class TestMatchesFilter:
    def test_all_matches_everything(self):
        applied_to = {"languages": ["ALL"], "frameworks": ["ALL"], "types": ["ALL"]}
        assert matches_filter(applied_to, ["java"], ["spring"], ["api"]) is True

    def test_filter_all_matches_everything(self):
        applied_to = {"languages": ["java"], "frameworks": ["spring"], "types": ["api"]}
        assert matches_filter(applied_to, ["ALL"], ["ALL"], ["ALL"]) is True

    def test_exact_match(self):
        applied_to = {"languages": ["java"], "frameworks": ["spring"], "types": ["api"]}
        assert matches_filter(applied_to, ["java"], ["spring"], ["api"]) is True

    def test_partial_overlap_within_dimension(self):
        applied_to = {"languages": ["java", "kotlin"], "frameworks": ["ALL"], "types": ["ALL"]}
        assert matches_filter(applied_to, ["java"], ["ALL"], ["ALL"]) is True

    def test_no_match_on_language(self):
        applied_to = {"languages": ["java"], "frameworks": ["ALL"], "types": ["ALL"]}
        assert matches_filter(applied_to, ["python"], ["ALL"], ["ALL"]) is False

    def test_no_match_on_framework(self):
        applied_to = {"languages": ["ALL"], "frameworks": ["spring"], "types": ["ALL"]}
        assert matches_filter(applied_to, ["ALL"], ["django"], ["ALL"]) is False

    def test_no_match_on_type(self):
        applied_to = {"languages": ["ALL"], "frameworks": ["ALL"], "types": ["api"]}
        assert matches_filter(applied_to, ["ALL"], ["ALL"], ["spa"]) is False

    def test_and_between_dimensions(self):
        applied_to = {"languages": ["java"], "frameworks": ["spring"], "types": ["api"]}
        # language matches but type doesn't
        assert matches_filter(applied_to, ["java"], ["spring"], ["spa"]) is False

    def test_or_within_dimension(self):
        applied_to = {"languages": ["java"], "frameworks": ["ALL"], "types": ["ALL"]}
        assert matches_filter(applied_to, ["java", "python"], ["ALL"], ["ALL"]) is True


class TestFilterRules:
    def test_filters_by_language(self):
        rules = [
            {"id": "A", "applied-to": {"languages": ["java"], "frameworks": ["ALL"], "types": ["ALL"]}},
            {"id": "B", "applied-to": {"languages": ["python"], "frameworks": ["ALL"], "types": ["ALL"]}},
        ]
        result = filter_rules(rules, ["java"], ["ALL"], ["ALL"])
        assert len(result) == 1
        assert result[0]["id"] == "A"

    def test_all_filter_includes_everything(self):
        rules = [
            {"id": "A", "applied-to": {"languages": ["java"], "frameworks": ["spring"], "types": ["api"]}},
            {"id": "B", "applied-to": {"languages": ["python"], "frameworks": ["django"], "types": ["cli"]}},
        ]
        result = filter_rules(rules, ["ALL"], ["ALL"], ["ALL"])
        assert len(result) == 2

    def test_empty_result(self):
        rules = [
            {"id": "A", "applied-to": {"languages": ["java"], "frameworks": ["spring"], "types": ["api"]}},
        ]
        result = filter_rules(rules, ["go"], ["ALL"], ["ALL"])
        assert len(result) == 0


class TestFilterAdrs:
    def test_filters_adrs_by_type(self):
        records = [
            {"id": "0001", "applied-to": {"languages": ["ALL"], "frameworks": ["ALL"], "types": ["api"]}},
            {"id": "0002", "applied-to": {"languages": ["ALL"], "frameworks": ["ALL"], "types": ["spa"]}},
        ]
        result = filter_adrs(records, ["ALL"], ["ALL"], ["api"])
        assert len(result) == 1
        assert result[0]["id"] == "0001"
