"""Validation logic for ADR and rule YAML sources."""

import re

from mdharness.constants import (
    ALLOWED_ADR_STATUSES,
    ALLOWED_FRAMEWORKS,
    ALLOWED_LANGUAGES,
    ALLOWED_LEVELS,
    ALLOWED_TYPES,
    CATEGORY_MAP,
)


def _validate_applied_to(applied_to, record_label):
    """Validate the applied-to block shared by ADRs and rules.

    Returns a tuple of (errors, warnings).
    """
    errors = []

    # applied-to must be a YAML mapping (dict), not a string or list.
    if not isinstance(applied_to, dict):
        errors.append(f"{record_label}: 'applied-to' must be a mapping")
        return errors, []

    # Check each of the three dimensions: languages, frameworks, types.
    for dimension, allowed in [
        ("languages", ALLOWED_LANGUAGES),
        ("frameworks", ALLOWED_FRAMEWORKS),
        ("types", ALLOWED_TYPES),
    ]:
        values = applied_to.get(dimension)

        # Every dimension is required.
        if values is None:
            errors.append(f"{record_label}: 'applied-to.{dimension}' is required")
            continue

        # Each dimension must be a non-empty list of values.
        if not isinstance(values, list) or len(values) == 0:
            errors.append(
                f"{record_label}: 'applied-to.{dimension}' must be a non-empty list"
            )
            continue

        # Each value must be one of the allowed constants for that dimension.
        for value in values:
            if value not in allowed:
                errors.append(
                    f"{record_label}: invalid {dimension} value '{value}'"
                )

        # "ALL" means every value, so listing specific values alongside it is contradictory.
        if "ALL" in values and len(values) > 1:
            errors.append(
                f"{record_label}: 'ALL' cannot appear alongside other values in {dimension}"
            )

    return errors, []


def validate_adrs(records, all_rule_ids=None):
    """Validate a list of ADR records.

    Returns a tuple of (errors, warnings).
    """
    errors = []
    warnings = []
    seen_ids = set()
    seen_codes = set()

    # Default to empty set so we can still check without loading rules first.
    if all_rule_ids is None:
        all_rule_ids = set()

    for index, record in enumerate(records):
        # Use a generic label until we know the ADR's actual ID.
        label = f"ADR record #{index + 1}"

        # --- Check that all required fields are present and non-empty ---
        required_fields = [
            "id", "code", "title", "status", "date", "decider",
            "rules-concerned", "applied-to", "context", "decision", "consequences",
        ]
        for field in required_fields:
            value = record.get(field)
            if value is None:
                errors.append(f"{label}: missing required field '{field}'")
            elif isinstance(value, str) and value.strip() == "":
                errors.append(f"{label}: field '{field}' must not be empty")

        # --- ID validation ---
        adr_id = record.get("id")
        if adr_id is not None:
            adr_id = str(adr_id)
            # Switch to a more descriptive label now that we know the ID.
            label = f"ADR {adr_id}"

            # IDs must be exactly 4 digits, zero-padded (e.g. "0001", "0042").
            if not re.match(r"^\d{4}$", adr_id):
                errors.append(f"{label}: id must be a zero-padded 4-digit string")

            # No two ADRs may share the same ID.
            if adr_id in seen_ids:
                errors.append(f"{label}: duplicate ADR id")
            seen_ids.add(adr_id)

        # --- Code validation ---
        code = record.get("code")
        if code is not None:
            # Codes must be lowercase slugs like "use-redis" or "api_versioning".
            if not re.match(r"^[a-z0-9][a-z0-9_-]*$", code):
                errors.append(
                    f"{label}: code must be lowercase alphanumeric with hyphens/underscores"
                )
            # No two ADRs may share the same code.
            if code in seen_codes:
                errors.append(f"{label}: duplicate ADR code '{code}'")
            seen_codes.add(code)

        # --- Date format ---
        date_val = record.get("date")
        if date_val is not None:
            date_str = str(date_val)
            # Dates must follow ISO format: YYYY-MM-DD.
            if not re.match(r"^\d{4}-\d{2}-\d{2}$", date_str):
                errors.append(f"{label}: date must be YYYY-MM-DD format")

        # --- Status validation ---
        status = record.get("status")
        if status is not None and status not in ALLOWED_ADR_STATUSES:
            errors.append(
                f"{label}: invalid status '{status}'. "
                f"Must be one of {ALLOWED_ADR_STATUSES}"
            )

        # --- applied-to validation (reuses shared helper) ---
        applied_to = record.get("applied-to")
        if applied_to is not None:
            at_errors, at_warnings = _validate_applied_to(applied_to, label)
            errors.extend(at_errors)
            warnings.extend(at_warnings)

        # --- Cross-reference: do the referenced rule IDs actually exist? ---
        rules_concerned = record.get("rules-concerned")
        if isinstance(rules_concerned, list):
            for rule_id in rules_concerned:
                # Missing references are warnings, not errors, so generation isn't blocked.
                if rule_id not in all_rule_ids:
                    warnings.append(
                        f"{label}: rules-concerned references unknown rule '{rule_id}'"
                    )

    return errors, warnings


def validate_rules(all_rules):
    """Validate all rules across the catalog.

    all_rules is a dict mapping category slug to list of rules.
    Returns a tuple of (errors, warnings).
    """
    errors = []
    warnings = []
    # Track IDs across ALL categories so duplicates are caught globally.
    seen_ids = set()

    for category_slug, rules in all_rules.items():
        # Make sure the YAML filename matches a known category from CATEGORY_MAP.
        category_info = CATEGORY_MAP.get(category_slug)
        if category_info is None:
            errors.append(f"Unknown category file: '{category_slug}-rules.yaml'")
            continue

        # The prefix that all rule IDs in this file must start with (e.g. "CMN", "SEC").
        expected_prefix = category_info[0]

        for index, rule in enumerate(rules):
            # Use a generic label until we know the rule's actual ID.
            label = f"Rule #{index + 1} in {category_slug}-rules.yaml"

            # --- Check that all required fields are present and non-empty ---
            required_fields = [
                "id", "title", "level", "owner", "applied-to",
                "since", "description", "content",
            ]
            for field in required_fields:
                value = rule.get(field)
                if value is None:
                    errors.append(f"{label}: missing required field '{field}'")
                elif isinstance(value, str) and value.strip() == "":
                    errors.append(f"{label}: field '{field}' must not be empty")

            # --- ID format and prefix validation ---
            rule_id = rule.get("id")
            if rule_id is not None:
                # Switch to a more descriptive label now that we know the ID.
                label = f"Rule {rule_id}"

                # IDs must follow the pattern PREFIX-NNNN (e.g. "CMN-0001", "SEC-0012").
                id_match = re.match(r"^([A-Z][\w-]*)-(\d{4})$", rule_id)
                if not id_match:
                    errors.append(
                        f"{label}: id must match <PREFIX>-<NNNN> format"
                    )
                else:
                    # The prefix portion must match what CATEGORY_MAP expects for this file.
                    prefix = id_match.group(1)
                    if prefix != expected_prefix:
                        errors.append(
                            f"{label}: prefix '{prefix}' does not match "
                            f"expected '{expected_prefix}' for {category_slug}-rules.yaml"
                        )

                # No two rules may share the same ID, even across different files.
                if rule_id in seen_ids:
                    errors.append(f"{label}: duplicate rule id")
                seen_ids.add(rule_id)

            # --- Level validation ---
            level = rule.get("level")
            if level is not None and level not in ALLOWED_LEVELS:
                errors.append(
                    f"{label}: invalid level '{level}'. Must be one of {ALLOWED_LEVELS}"
                )

            # "waivable" defaults to True at generation time, so missing it is not an error.

            # --- applied-to validation (reuses shared helper) ---
            applied_to = rule.get("applied-to")
            if applied_to is not None:
                at_errors, at_warnings = _validate_applied_to(applied_to, label)
                errors.extend(at_errors)
                warnings.extend(at_warnings)

    return errors, warnings


def collect_all_rule_ids(all_rules):
    """Collect all rule IDs from the catalog for cross-reference validation."""
    ids = set()
    for rules in all_rules.values():
        for rule in rules:
            rule_id = rule.get("id")
            if rule_id is not None:
                ids.add(rule_id)
    return ids
