"""Filter rules and ADRs by languages, frameworks, and types."""


def matches_filter(applied_to, languages_filter, frameworks_filter, types_filter):
    """Check if an applied-to block matches the given filter.

    Filter semantics:
    - AND between dimensions (all three must match).
    - OR within each dimension (any overlap suffices).
    - ALL in the record means it matches any filter value for that dimension.
    - ALL in the filter means any record value matches for that dimension.
    """
    record_languages = applied_to.get("languages", [])
    record_frameworks = applied_to.get("frameworks", [])
    record_types = applied_to.get("types", [])

    # Check each dimension independently.
    languages_match = _dimension_matches(record_languages, languages_filter)
    frameworks_match = _dimension_matches(record_frameworks, frameworks_filter)
    types_match = _dimension_matches(record_types, types_filter)

    # All three dimensions must match (AND logic between dimensions).
    return languages_match and frameworks_match and types_match


def _dimension_matches(record_values, filter_values):
    """Check if a single dimension matches."""
    # "ALL" in the user's filter means "don't filter this dimension at all".
    if "ALL" in filter_values:
        return True

    # "ALL" in the record means the record applies to every possible value.
    if "ALL" in record_values:
        return True

    # Otherwise, check for any overlap (OR logic within a dimension).
    record_set = set(record_values)
    filter_set = set(filter_values)
    return len(record_set.intersection(filter_set)) > 0


def filter_rules(rules, languages_filter, frameworks_filter, types_filter):
    """Filter a list of rules by the given dimensions."""
    matched = []
    for rule in rules:
        applied_to = rule.get("applied-to", {})
        if matches_filter(applied_to, languages_filter, frameworks_filter, types_filter):
            matched.append(rule)
    return matched


def filter_adrs(records, languages_filter, frameworks_filter, types_filter):
    """Filter a list of ADR records by the given dimensions."""
    matched = []
    for record in records:
        applied_to = record.get("applied-to", {})
        if matches_filter(applied_to, languages_filter, frameworks_filter, types_filter):
            matched.append(record)
    return matched
