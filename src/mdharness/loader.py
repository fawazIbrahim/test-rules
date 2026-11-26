"""Load and parse YAML source files for ADRs and rules."""

import os
import yaml


def load_adr_file(source_dir):
    """Load adr.yaml and return the list of ADR records."""
    adr_path = os.path.join(source_dir, "adr.yaml")

    # If adr.yaml doesn't exist, return an empty list instead of crashing.
    if not os.path.exists(adr_path):
        return []

    with open(adr_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    # Handle empty files or files missing the top-level "records" key.
    if data is None or "records" not in data:
        return []

    return data["records"]


def load_rules_file(file_path):
    """Load a single rules YAML file and return the list of rules."""
    with open(file_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    # Handle empty files or files missing the top-level "rules" key.
    if data is None or "rules" not in data:
        return []

    return data["rules"]


def load_all_rules(source_dir):
    """Load all rules YAML files from the rules-catalog directory.

    Returns a dict mapping category slug to list of rules.
    The category slug is the filename without '-rules.yaml'.
    """
    catalog_dir = os.path.join(source_dir, "rules-catalog")

    # If the rules-catalog directory doesn't exist, there are no rules to load.
    if not os.path.isdir(catalog_dir):
        return {}

    all_rules = {}

    # Process files in sorted order so output is deterministic.
    for filename in sorted(os.listdir(catalog_dir)):
        # Only process files that follow the naming convention: <slug>-rules.yaml
        if not filename.endswith("-rules.yaml"):
            continue

        # Extract category slug, e.g. "common-rules.yaml" -> "common"
        category_slug = filename.replace("-rules.yaml", "")
        file_path = os.path.join(catalog_dir, filename)
        rules = load_rules_file(file_path)
        all_rules[category_slug] = rules

    return all_rules
