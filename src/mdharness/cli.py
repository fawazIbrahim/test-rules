"""CLI entry point for mdharness."""

import json
import os
import shutil
import sys

import click
import yaml
from tabulate import tabulate

from mdharness import __version__
from mdharness.constants import CATEGORY_MAP
from mdharness.filtering import filter_adrs, filter_rules
from mdharness.generator import write_adr_files, write_rules_files
from mdharness.loader import load_adr_file, load_all_rules
from mdharness.validation import collect_all_rule_ids, validate_adrs, validate_rules


def _parse_comma_list(value):
    """Parse a comma-separated string into a list."""
    # When no filter is provided, default to "ALL" (match everything).
    if value is None or value.strip() == "":
        return ["ALL"]
    # Split on commas and strip whitespace from each item.
    return [v.strip() for v in value.split(",") if v.strip()]


@click.group()
@click.option("--source", "-s", default="./source", help="Path to source directory.")
@click.option("--target", "-t", default="./target", help="Path to target directory.")
@click.option("--verbose", "-v", is_flag=True, default=False, help="Verbose output.")
@click.version_option(version=__version__)
@click.pass_context
def main(ctx, source, target, verbose):
    """mdharness — generate filtered Markdown from YAML sources."""
    ctx.ensure_object(dict)
    ctx.obj["source"] = source
    ctx.obj["target"] = target
    ctx.obj["verbose"] = verbose


# ---------------------------------------------------------------------------
# generate
# ---------------------------------------------------------------------------

@main.command()
@click.option("--languages", "-l", default=None, help="Comma-separated languages.")
@click.option("--frameworks", "-f", default=None, help="Comma-separated frameworks.")
@click.option("--types", "-T", default=None, help="Comma-separated application types.")
@click.option("--clean", is_flag=True, default=False, help="Remove target dir first.")
@click.option("--dry-run", is_flag=True, default=False, help="Preview without writing.")
@click.pass_context
def generate(ctx, languages, frameworks, types, clean, dry_run):
    """Generate filtered Markdown files from YAML sources."""
    source_dir = ctx.obj["source"]
    target_dir = ctx.obj["target"]
    verbose = ctx.obj["verbose"]

    # Parse the comma-separated filter options into lists.
    lang_filter = _parse_comma_list(languages)
    fw_filter = _parse_comma_list(frameworks)
    type_filter = _parse_comma_list(types)

    # Step 1: Load all YAML sources.
    adr_records = load_adr_file(source_dir)
    all_rules = load_all_rules(source_dir)

    # Step 2: Validate everything before generating any output.
    all_rule_ids = collect_all_rule_ids(all_rules)
    adr_errors, adr_warnings = validate_adrs(adr_records, all_rule_ids)
    rule_errors, rule_warnings = validate_rules(all_rules)

    errors = adr_errors + rule_errors
    warnings = adr_warnings + rule_warnings

    # Print warnings to stderr (they don't block generation).
    for warning in warnings:
        click.echo(f"WARNING: {warning}", err=True)

    # Errors are fatal — abort before writing any files.
    if len(errors) > 0:
        for error in errors:
            click.echo(f"ERROR: {error}", err=True)
        click.echo(f"\n{len(errors)} error(s) found. Generation aborted.", err=True)
        sys.exit(1)

    # Step 3: Filter ADRs and rules by the requested dimensions.
    filtered_adrs = filter_adrs(adr_records, lang_filter, fw_filter, type_filter)
    filtered_rules = {}
    total_included = 0
    total_excluded = 0

    for category_slug, rules in all_rules.items():
        matched = filter_rules(rules, lang_filter, fw_filter, type_filter)
        filtered_rules[category_slug] = matched
        total_included += len(matched)
        total_excluded += len(rules) - len(matched)

    # In dry-run mode, just print what would be generated and exit.
    if dry_run:
        click.echo("Dry run — no files will be written.\n")
        if len(filtered_adrs) > 0:
            click.echo(f"ADR files to generate: {len(filtered_adrs)}")
            for record in filtered_adrs:
                click.echo(f"  adr-{record['id']}-{record['code']}.md")
        rule_files = [slug for slug, rules in filtered_rules.items() if len(rules) > 0]
        if len(rule_files) > 0:
            click.echo(f"Rule files to generate: {len(rule_files)}")
            for slug in rule_files:
                click.echo(f"  {slug}.md ({len(filtered_rules[slug])} rules)")
                for rule in filtered_rules[slug]:
                    click.echo(f"    - {rule.get('id', '???')}: {rule.get('title', '')}")
        click.echo(f"\nRules: {total_included} included, {total_excluded} excluded.")
        return

    # Step 4: Optionally wipe the target directory for a fresh start.
    if clean and os.path.exists(target_dir):
        shutil.rmtree(target_dir)

    # Step 5: Write the filtered Markdown files to disk.
    adr_files = write_adr_files(filtered_adrs, target_dir)
    rule_files = write_rules_files(filtered_rules, target_dir)

    # Print a summary of what was generated.
    files_generated = len(adr_files) + len(rule_files)
    click.echo(f"Generated {files_generated} file(s).")
    click.echo(f"  ADR files: {len(adr_files)}")
    click.echo(f"  Rule files: {len(rule_files)}")
    click.echo(f"  Rules included: {total_included}, excluded: {total_excluded}")

    # In verbose mode, list each generated file path.
    if verbose:
        for name in adr_files:
            click.echo(f"  -> docs/adr/{name}")
        for name in rule_files:
            click.echo(f"  -> rules/{name}")


# ---------------------------------------------------------------------------
# validate
# ---------------------------------------------------------------------------

@main.command()
@click.pass_context
def validate(ctx):
    """Validate source YAML files without generating output."""
    source_dir = ctx.obj["source"]

    adr_records = load_adr_file(source_dir)
    all_rules = load_all_rules(source_dir)

    all_rule_ids = collect_all_rule_ids(all_rules)
    adr_errors, adr_warnings = validate_adrs(adr_records, all_rule_ids)
    rule_errors, rule_warnings = validate_rules(all_rules)

    errors = adr_errors + rule_errors
    warnings = adr_warnings + rule_warnings

    for warning in warnings:
        click.echo(f"WARNING: {warning}", err=True)
    for error in errors:
        click.echo(f"ERROR: {error}", err=True)

    if len(errors) > 0:
        click.echo(f"\n{len(errors)} error(s) found.", err=True)
        sys.exit(1)
    else:
        click.echo("Validation passed. No errors found.")
        if len(warnings) > 0:
            click.echo(f"{len(warnings)} warning(s).")


# ---------------------------------------------------------------------------
# rules group
# ---------------------------------------------------------------------------

@main.group()
@click.pass_context
def rules(ctx):
    """Rule management commands."""
    pass


def _load_and_flatten_rules(source_dir):
    """Load all rules and return a flat list with category_slug added."""
    all_rules = load_all_rules(source_dir)
    flat = []
    for category_slug, rule_list in all_rules.items():
        for rule in rule_list:
            # Tag each rule with its category so we can filter/display by category later.
            # The underscore prefix marks it as an internal field (not from the YAML source).
            rule["_category_slug"] = category_slug
            flat.append(rule)
    return flat


def _apply_rule_filters(rules_list, id_filter, title_filter, level_filter,
                        languages, frameworks, types, category, waivable, owner):
    """Apply search filters to a flat list of rules."""
    result = []

    for rule in rules_list:
        # Each filter below skips the rule (continue) if it doesn't match.
        # A None filter means "not specified" and is ignored.

        # ID filter: matches if the rule ID starts with or equals the filter string.
        if id_filter is not None:
            rule_id = rule.get("id", "")
            if not rule_id.startswith(id_filter) and rule_id != id_filter:
                continue

        # Title filter: case-insensitive substring search.
        if title_filter is not None:
            rule_title = rule.get("title", "")
            if title_filter.lower() not in rule_title.lower():
                continue

        # Level filter: exact match (MUST or SHOULD).
        if level_filter is not None:
            if rule.get("level") != level_filter:
                continue

        # Category filter: exact match on the category slug.
        if category is not None:
            if rule.get("_category_slug") != category:
                continue

        # Waivable filter: boolean match (defaults to True if not set in YAML).
        if waivable is not None:
            rule_waivable = rule.get("waivable", True)
            if rule_waivable != waivable:
                continue

        # Owner filter: case-insensitive substring search.
        if owner is not None:
            rule_owner = rule.get("owner", "")
            if owner.lower() not in rule_owner.lower():
                continue

        # Dimension filters (languages, frameworks, types) reuse the shared filtering logic.
        applied_to = rule.get("applied-to", {})
        lang_filter = _parse_comma_list(languages)
        fw_filter = _parse_comma_list(frameworks)
        type_filter = _parse_comma_list(types)

        from mdharness.filtering import matches_filter
        if not matches_filter(applied_to, lang_filter, fw_filter, type_filter):
            continue

        # Rule passed all active filters.
        result.append(rule)

    return result


@rules.command("search")
@click.option("--id", "id_filter", default=None, help="Filter by rule ID.")
@click.option("--title", "title_filter", default=None, help="Search in titles.")
@click.option("--level", default=None, type=click.Choice(["MUST", "SHOULD"]))
@click.option("--languages", "-l", default=None, help="Filter by languages.")
@click.option("--frameworks", "-f", default=None, help="Filter by frameworks.")
@click.option("--types", "-T", default=None, help="Filter by types.")
@click.option("--category", "-c", default=None, help="Filter by category slug.")
@click.option("--waivable", default=None, help="Filter by waivable (true/false).")
@click.option("--owner", default=None, help="Filter by owner.")
@click.option("--format", "fmt", default="table",
              type=click.Choice(["table", "json", "yaml", "ids"]))
@click.pass_context
def rules_search(ctx, id_filter, title_filter, level, languages, frameworks,
                 types, category, waivable, owner, fmt):
    """Search rules by criteria."""
    source_dir = ctx.obj["source"]
    flat_rules = _load_and_flatten_rules(source_dir)

    # Convert the waivable string option ("true"/"false") to a Python boolean.
    waivable_bool = None
    if waivable is not None:
        waivable_bool = waivable.lower() == "true"

    matched = _apply_rule_filters(
        flat_rules, id_filter, title_filter, level,
        languages, frameworks, types, category, waivable_bool, owner,
    )

    # Output in the requested format.
    if fmt == "ids":
        # Just print one rule ID per line.
        for rule in matched:
            click.echo(rule["id"])
    elif fmt == "json":
        # Exclude internal fields (prefixed with _) from the output.
        output = []
        for rule in matched:
            entry = {k: v for k, v in rule.items() if not k.startswith("_")}
            output.append(entry)
        click.echo(json.dumps(output, indent=2, default=str))
    elif fmt == "yaml":
        # Exclude internal fields (prefixed with _) from the output.
        output = []
        for rule in matched:
            entry = {k: v for k, v in rule.items() if not k.startswith("_")}
            output.append(entry)
        click.echo(yaml.dump(output, default_flow_style=False, sort_keys=False))
    else:
        # Default: display as an ASCII table.
        rows = []
        for rule in matched:
            rows.append([
                rule.get("id", ""),
                rule.get("title", ""),
                rule.get("level", ""),
                rule.get("_category_slug", ""),
                str(rule.get("waivable", True)),
            ])
        headers = ["ID", "Title", "Level", "Category", "Waivable"]
        click.echo(tabulate(rows, headers=headers, tablefmt="simple"))


@rules.command("count")
@click.option("--id", "id_filter", default=None)
@click.option("--title", "title_filter", default=None)
@click.option("--level", default=None, type=click.Choice(["MUST", "SHOULD"]))
@click.option("--languages", "-l", default=None)
@click.option("--frameworks", "-f", default=None)
@click.option("--types", "-T", default=None)
@click.option("--category", "-c", default=None)
@click.option("--waivable", default=None)
@click.option("--owner", default=None)
@click.option("--group-by", "group_by", default=None,
              type=click.Choice(["category", "level", "language", "framework", "type", "owner"]))
@click.pass_context
def rules_count(ctx, id_filter, title_filter, level, languages, frameworks,
                types, category, waivable, owner, group_by):
    """Count rules matching criteria."""
    source_dir = ctx.obj["source"]
    flat_rules = _load_and_flatten_rules(source_dir)

    waivable_bool = None
    if waivable is not None:
        waivable_bool = waivable.lower() == "true"

    matched = _apply_rule_filters(
        flat_rules, id_filter, title_filter, level,
        languages, frameworks, types, category, waivable_bool, owner,
    )

    # Without --group-by, just print the total count.
    if group_by is None:
        click.echo(f"Total: {len(matched)}")
        return

    # Group the matched rules by the requested dimension and count each group.
    groups = {}
    for rule in matched:
        if group_by == "category":
            key = rule.get("_category_slug", "unknown")
            groups[key] = groups.get(key, 0) + 1
        elif group_by == "level":
            key = rule.get("level", "unknown")
            groups[key] = groups.get(key, 0) + 1
        elif group_by == "owner":
            key = rule.get("owner", "unknown")
            groups[key] = groups.get(key, 0) + 1
        elif group_by == "language":
            # A rule can target multiple languages, so it counts in each group.
            for lang in rule.get("applied-to", {}).get("languages", []):
                groups[lang] = groups.get(lang, 0) + 1
        elif group_by == "framework":
            # A rule can target multiple frameworks, so it counts in each group.
            for fw in rule.get("applied-to", {}).get("frameworks", []):
                groups[fw] = groups.get(fw, 0) + 1
        elif group_by == "type":
            # A rule can target multiple types, so it counts in each group.
            for t in rule.get("applied-to", {}).get("types", []):
                groups[t] = groups.get(t, 0) + 1

    # Display the grouped counts as an ASCII table, sorted alphabetically.
    rows = [[key, count] for key, count in sorted(groups.items())]
    click.echo(tabulate(rows, headers=[group_by.title(), "Count"], tablefmt="simple"))


@rules.command("show")
@click.argument("rule_id")
@click.pass_context
def rules_show(ctx, rule_id):
    """Display full details of a single rule by ID."""
    source_dir = ctx.obj["source"]
    flat_rules = _load_and_flatten_rules(source_dir)

    # Search for the rule by exact ID match.
    found = None
    for rule in flat_rules:
        if rule.get("id") == rule_id:
            found = rule
            break

    if found is None:
        click.echo(f"Rule '{rule_id}' not found.", err=True)
        sys.exit(2)

    # Render and display the rule as Markdown.
    from mdharness.generator import generate_rule_markdown
    click.echo(generate_rule_markdown(found))


# ---------------------------------------------------------------------------
# adr group
# ---------------------------------------------------------------------------

@main.group()
@click.pass_context
def adr(ctx):
    """ADR management commands."""
    pass


@adr.command("list")
@click.option("--status", default=None, help="Filter by status.")
@click.option("--languages", "-l", default=None, help="Filter by languages.")
@click.option("--frameworks", "-f", default=None, help="Filter by frameworks.")
@click.option("--types", "-T", default=None, help="Filter by types.")
@click.option("--format", "fmt", default="table",
              type=click.Choice(["table", "json", "yaml"]))
@click.pass_context
def adr_list(ctx, status, languages, frameworks, types, fmt):
    """List all ADRs."""
    source_dir = ctx.obj["source"]
    records = load_adr_file(source_dir)

    # Apply dimension filters (languages, frameworks, types).
    lang_filter = _parse_comma_list(languages)
    fw_filter = _parse_comma_list(frameworks)
    type_filter = _parse_comma_list(types)
    records = filter_adrs(records, lang_filter, fw_filter, type_filter)

    # Apply the optional status filter (e.g. show only "Accepted" ADRs).
    if status is not None:
        records = [r for r in records if r.get("status") == status]

    # Output in the requested format.
    if fmt == "json":
        click.echo(json.dumps(records, indent=2, default=str))
    elif fmt == "yaml":
        click.echo(yaml.dump(records, default_flow_style=False, sort_keys=False))
    else:
        # Default: display as an ASCII table.
        rows = []
        for r in records:
            rows.append([
                str(r.get("id", "")),
                r.get("title", ""),
                r.get("status", ""),
                str(r.get("date", "")),
            ])
        headers = ["ID", "Title", "Status", "Date"]
        click.echo(tabulate(rows, headers=headers, tablefmt="simple"))


@adr.command("show")
@click.argument("adr_id")
@click.pass_context
def adr_show(ctx, adr_id):
    """Display full details of a single ADR by ID."""
    source_dir = ctx.obj["source"]
    records = load_adr_file(source_dir)

    # Search for the ADR by exact ID match.
    found = None
    for record in records:
        if str(record.get("id")) == adr_id:
            found = record
            break

    if found is None:
        click.echo(f"ADR '{adr_id}' not found.", err=True)
        sys.exit(2)

    # Render and display the ADR as Markdown.
    from mdharness.generator import generate_adr_markdown
    click.echo(generate_adr_markdown(found))


if __name__ == "__main__":
    main()
