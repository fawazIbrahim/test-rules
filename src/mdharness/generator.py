"""Generate Markdown files from validated and filtered YAML data."""

import os

from mdharness.constants import CATEGORY_MAP


def generate_adr_markdown(record):
    """Generate Markdown content for a single ADR record."""
    # Extract all fields from the ADR record.
    adr_id = str(record["id"])
    title = record["title"]
    status = record["status"]
    date = str(record["date"])
    decider = record["decider"]

    # Format the rules-concerned list as a bracketed string like "[CMN-0001, SEC-0003]".
    rules_concerned = record.get("rules-concerned", [])
    if isinstance(rules_concerned, list) and len(rules_concerned) > 0:
        rules_str = "[" + ", ".join(str(r) for r in rules_concerned) + "]"
    else:
        rules_str = "[]"

    # Strip trailing whitespace from free-text blocks to keep output clean.
    context = record.get("context", "").rstrip()
    decision = record.get("decision", "").rstrip()
    consequences = record.get("consequences", "").rstrip()

    # Build the Markdown output line by line.
    lines = []
    # Title as H1 with the ADR number prefix.
    lines.append(f"# {adr_id}. {title}")
    # Frontmatter-style metadata block between --- delimiters.
    lines.append("---")
    lines.append(f"status: {status}")
    lines.append(f"date: {date}")
    lines.append(f"decider: {decider}")
    lines.append(f"rules-concerned: {rules_str}")
    lines.append("---")
    lines.append("")
    # Each section gets its own H2 heading.
    lines.append("## Context")
    lines.append(context)
    lines.append("")
    lines.append("## Decision")
    lines.append(decision)
    lines.append("")
    lines.append("## Consequences")
    lines.append(consequences)
    lines.append("")

    return "\n".join(lines)


def generate_rule_markdown(rule):
    """Generate Markdown content for a single rule (H2 section)."""
    rule_id = rule["id"]
    title = rule["title"]
    level = rule["level"]
    owner = rule["owner"]
    # Default waivable to True if not specified in the YAML source.
    waivable = rule.get("waivable", True)
    since = rule["since"]
    description = rule.get("description", "").rstrip()
    content = rule.get("content", "").rstrip()

    # Build the Markdown output line by line.
    lines = []
    # Title as H2 with the rule ID prefix (rules are sections within a category file).
    lines.append(f"## {rule_id}. {title}")
    # Metadata block between --- delimiters.
    lines.append("---")
    lines.append(f"level: {level}")
    lines.append(f"owner: {owner}")
    lines.append(f"waivable: {str(waivable).lower()}")
    lines.append(f"since: {since}")
    lines.append("---")
    lines.append("")
    # Description and content are free-text blocks.
    lines.append(description)
    lines.append("")
    lines.append(content)
    lines.append("")

    return "\n".join(lines)


def generate_rules_file_markdown(category_slug, rules):
    """Generate full Markdown content for a category rules file."""
    # Look up the human-readable category name (e.g. "Common", "Security").
    category_info = CATEGORY_MAP.get(category_slug)
    if category_info is None:
        # Fallback: convert the slug itself to title case (e.g. "error-handling" -> "Error Handling").
        category_name = category_slug.replace("-", " ").title()
    else:
        category_name = category_info[1]

    # Start the file with an H1 heading, then append each rule as an H2 section.
    lines = []
    lines.append(f"# Rules of {category_name}")
    lines.append("")

    for rule in rules:
        lines.append(generate_rule_markdown(rule))

    return "\n".join(lines)


def write_adr_files(records, target_dir):
    """Write ADR Markdown files to the target directory."""
    # ADR files go into a dedicated "adr" subdirectory.
    adr_dir = os.path.join(target_dir, "adr")
    os.makedirs(adr_dir, exist_ok=True)

    written = []
    for record in records:
        adr_id = str(record["id"])
        code = record["code"]
        # Filename follows the pattern: adr-<id>-<code>.md (e.g. "adr-0001-use-redis.md").
        filename = f"adr-{adr_id}-{code}.md"
        file_path = os.path.join(adr_dir, filename)

        content = generate_adr_markdown(record)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        written.append(filename)

    return written


def write_rules_files(all_filtered_rules, target_dir):
    """Write rules Markdown files to the target directory."""
    # Rule files go into a dedicated "rules" subdirectory.
    rules_dir = os.path.join(target_dir, "rules")
    os.makedirs(rules_dir, exist_ok=True)

    written = []
    for category_slug, rules in all_filtered_rules.items():
        # Skip categories that have no matching rules after filtering.
        if len(rules) == 0:
            continue

        # Filename matches the category slug (e.g. "common.md", "security.md").
        filename = f"{category_slug}.md"
        file_path = os.path.join(rules_dir, filename)

        content = generate_rules_file_markdown(category_slug, rules)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        written.append(filename)

    return written
