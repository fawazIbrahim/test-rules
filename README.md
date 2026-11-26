# mdharness

A Python CLI that generates filtered Markdown files (ADRs and rules) from YAML sources, designed to provide coding agents with structured project rules and architectural decisions.

## How It Works

```
source/                              target/
  adr.yaml              -->            docs/adr/adr-0001-*.md
  rules-catalog/                       rules/
    common-rules.yaml      -->           common.md
    security-rules.yaml    -->           security.md
    testing-rules.yaml     -->           testing.md
    ...                                  ...
```

YAML is the single source of truth. The CLI reads it, validates it, filters by language/framework/app type, and writes Markdown.

## Features

- **Generate** filtered Markdown output for a specific stack (e.g. Java + Spring + API)
- **Validate** YAML sources without generating
- **Search** rules by ID, title, level, category, applicability, owner
- **Count** rules with group-by support
- **List/show** ADRs with status and applicability filters

## Filtering

Rules and ADRs declare where they apply across three dimensions:

```yaml
applied-to:
  languages: [java, kotlin]
  frameworks: [spring]
  types: [api, worker]
```

- **Between** dimensions: AND (all must match)
- **Within** a dimension: OR (any match suffices)
- `ALL` = wildcard for that dimension

## Installation

Requires Python 3.10+.

```bash
cd <project-root>
pip install -e .
```

This installs the dependencies (click, pyyaml, tabulate) and registers the `mdharness` command. pip generates a small `.exe` wrapper (Windows) or shell script (macOS/Linux) in your Python `Scripts/` directory that calls `mdharness.cli:main()`.

**Windows note:** Some environments (corporate machines, Windows Application Control policies) block `.exe` files that pip installs into `Scripts/`. If `mdharness` fails with an "Application Control policy" error, use the included wrapper instead:

```bash
.\mdharness.cmd generate --languages java --frameworks spring --types api
```

This calls `python -m mdharness` under the hood, which bypasses the `.exe` restriction. You can also call `python -m mdharness` directly from anywhere:

```bash
python -m mdharness generate --languages java --frameworks spring --types api
```

## Usage

### Global Options

Global options go **before** the command name.

```bash
# Use a custom source directory (-s is the short form)
mdharness --source ./my-source generate
mdharness -s ./my-source generate

# Use a custom target directory (-t is the short form)
mdharness --target ./my-output generate
mdharness -t ./my-output generate

# Combine custom source and target
mdharness --source ./my-source --target ./my-output generate

# Enable verbose output (-v is the short form) — lists each generated file path
mdharness --verbose generate --languages java
mdharness -v generate --languages java

# Print version
mdharness --version

# Print help (works on any command too)
mdharness --help
mdharness generate --help
mdharness rules search --help
```

### `mdharness generate`

Generate filtered Markdown files from YAML sources.

```bash
# Generate everything (no filters, all rules and ADRs included)
mdharness generate

# Filter by language (-l is the short form)
mdharness generate --languages java
mdharness generate -l typescript

# Filter by multiple languages (comma-separated)
mdharness generate --languages java,kotlin

# Filter by framework (-f is the short form)
mdharness generate --frameworks spring
mdharness generate -f react

# Filter by multiple frameworks
mdharness generate --frameworks spring,quarkus

# Filter by application type (-T is the short form)
mdharness generate --types api
mdharness generate -T spa,ssr

# Combine all three dimensions (AND between them)
mdharness generate --languages java --frameworks spring --types api
mdharness generate -l typescript -f react -T spa

# Preview what would be generated without writing files (lists every rule)
mdharness generate --dry-run
mdharness generate --languages python --frameworks fastapi --dry-run

# Remove the target directory before generating (fresh output)
mdharness generate --clean

# Combine clean and filters
mdharness generate --clean --languages go --types api

# Combine dry-run with filters
mdharness generate --languages typescript --frameworks react --dry-run

# Full example with all options
mdharness -v -s ./source -t ./output generate --languages java --frameworks spring --types api --clean
```

### `mdharness validate`

Validate source YAML files without generating any output. Exits with code 0 on success, 1 on errors.

```bash
# Validate using the default source directory (./source)
mdharness validate

# Validate a custom source directory
mdharness --source ./my-harness/source validate
mdharness -s ./my-harness/source validate
```

### `mdharness rules search`

Search rules by various criteria. All filters are optional and combined with AND logic.

```bash
# Search by rule ID (exact match or prefix)
mdharness rules search --id SEC-0001
mdharness rules search --id SEC

# Search by title (substring, case-insensitive)
mdharness rules search --title "logging"
mdharness rules search --title "database"

# Search by level (MUST or SHOULD)
mdharness rules search --level MUST
mdharness rules search --level SHOULD

# Search by category slug (-c is the short form)
mdharness rules search --category security
mdharness rules search -c testing

# Search by waivable status
mdharness rules search --waivable true
mdharness rules search --waivable false

# Search by owner (substring, case-insensitive)
mdharness rules search --owner "platform"

# Search by language (-l is the short form)
mdharness rules search --languages java
mdharness rules search -l typescript,python

# Search by framework (-f is the short form)
mdharness rules search --frameworks spring
mdharness rules search -f react,angular

# Search by application type (-T is the short form)
mdharness rules search --types api
mdharness rules search -T spa,ssr

# Combine multiple filters
mdharness rules search --category security --level MUST --languages java
mdharness rules search --title "test" --level MUST --waivable false

# Output as JSON
mdharness rules search --format json
mdharness rules search --level MUST --format json

# Output as YAML
mdharness rules search --format yaml
mdharness rules search --category observability --format yaml

# Output just the rule IDs (one per line, useful for scripting)
mdharness rules search --format ids
mdharness rules search --level MUST --format ids

# Full example with all filters and format
mdharness rules search --id SEC --title "input" --level MUST --category security --languages java --frameworks spring --types api --waivable true --owner "security" --format json
```

### `mdharness rules count`

Count rules matching criteria. Accepts the same filter options as `rules search`, plus `--group-by`.

```bash
# Total count of all rules
mdharness rules count

# Count with filters (same options as rules search)
mdharness rules count --level MUST
mdharness rules count --languages python
mdharness rules count --category security --level MUST

# Group by category
mdharness rules count --group-by category

# Group by level
mdharness rules count --group-by level

# Group by language
mdharness rules count --group-by language

# Group by framework
mdharness rules count --group-by framework

# Group by application type
mdharness rules count --group-by type

# Group by owner
mdharness rules count --group-by owner

# Combine filters with group-by
mdharness rules count --level MUST --group-by category
mdharness rules count --languages java --group-by framework
mdharness rules count --waivable false --group-by level
```

### `mdharness rules show`

Display the full Markdown details of a single rule by its exact ID.

```bash
mdharness rules show SEC-0001
mdharness rules show CMN-0003
mdharness rules show TEST-0001

# With a custom source directory
mdharness --source ./my-source rules show ARCH-0005
```

### `mdharness adr list`

List ADRs with their ID, title, status, and date.

```bash
# List all ADRs
mdharness adr list

# Filter by status
mdharness adr list --status Accepted
mdharness adr list --status Proposed
mdharness adr list --status Deprecated
mdharness adr list --status Superseded

# Filter by language (-l is the short form)
mdharness adr list --languages java
mdharness adr list -l typescript

# Filter by framework (-f is the short form)
mdharness adr list --frameworks spring
mdharness adr list -f react

# Filter by application type (-T is the short form)
mdharness adr list --types api
mdharness adr list -T spa,ssr

# Combine filters
mdharness adr list --status Accepted --languages java --frameworks spring --types api

# Output as JSON
mdharness adr list --format json
mdharness adr list --status Accepted --format json

# Output as YAML
mdharness adr list --format yaml
mdharness adr list --languages python --format yaml
```

### `mdharness adr show`

Display the full Markdown details of a single ADR by its ID.

```bash
mdharness adr show 0001
mdharness adr show 0012

# With a custom source directory
mdharness --source ./my-source adr show 0005
```

## Project Structure

```
specs/          Specifications (source of truth for what to build)
source/         YAML source files (ADRs + rules catalog)
target/         Generated Markdown output
src/mdharness/  Python source code
tests/          Test suite (pytest)
```

## Development

This project follows **spec-driven development**. See [`AGENTS.md`](AGENTS.md) for the workflow and [`specs/`](specs/) for all specifications.

```bash
# Install in editable mode with test dependencies
pip install -e .
pip install pytest

# Run tests
python -m pytest tests/ -v
```
