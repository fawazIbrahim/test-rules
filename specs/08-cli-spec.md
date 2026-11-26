# CLI Specification

## Overview

A Python CLI tool that generates filtered Markdown output from YAML sources and provides rule/ADR management utilities.

## Installation

The CLI is distributed as a Python package and installed via pip. The entry point command is `mdharness`.

## Global Options

| Option       | Short | Description                                      | Default          |
|--------------|-------|--------------------------------------------------|------------------|
| `--source`   | `-s`  | Path to the source directory                     | `./source`       |
| `--target`   | `-t`  | Path to the target output directory              | `./target`       |
| `--verbose`  | `-v`  | Enable verbose output                            | `false`          |
| `--version`  |       | Print version and exit                           |                  |
| `--help`     | `-h`  | Print help and exit                              |                  |

---

## Commands

### `mdharness generate`

Generate the target directory with filtered Markdown files from YAML sources.

#### Options

| Option          | Short | Description                                                     | Default |
|-----------------|-------|-----------------------------------------------------------------|---------|
| `--languages`   | `-l`  | Comma-separated list of languages to include                    | `ALL`   |
| `--frameworks`  | `-f`  | Comma-separated list of frameworks to include                   | `ALL`   |
| `--types`       | `-T`  | Comma-separated list of application types to include            | `ALL`   |
| `--clean`       |       | Remove existing target directory before generating              | `false` |
| `--dry-run`     |       | Show what would be generated without writing files. Lists each ADR filename and each rule ID + title per category. | `false` |

#### Behavior

1. Validate all source YAML files. Stop on errors, warn on warnings.
2. Filter and generate ADR files into `target/docs/adr/`, applying the same `languages`, `frameworks`, `types` filter as rules. Only ADRs matching the filter are generated.
3. For each rules YAML file, filter rules by the provided `languages`, `frameworks`, and `types`:
   - A rule is included if all three dimensions match the filter (AND between dimensions).
   - Within each dimension, the filter matches if any value overlaps (OR).
   - A rule with `ALL` in a dimension always matches that dimension.
   - A filter set to `ALL` (default) matches any value in that dimension.
4. Generate one Markdown file per category, containing only the matched rules.
5. Skip a category file entirely if no rules match the filter.
6. Print a summary: number of files generated, number of rules included/excluded.

#### Examples

```bash
# Generate everything (no filter)
mdharness generate

# Generate only rules applicable to Java + Spring APIs
mdharness generate --languages java --frameworks spring --types api

# Generate for TypeScript projects, any framework, SPA or SSR types
mdharness generate --languages typescript --types spa,ssr

# Dry run to preview what would be generated
mdharness generate --languages python --frameworks fastapi --dry-run
```

---

### `mdharness validate`

Validate source YAML files without generating output.

#### Behavior

1. Run all validation rules from [05-validation-rules.md](05-validation-rules.md).
2. Report errors and warnings.
3. Exit code 0 if no errors, 1 if errors found.

#### Examples

```bash
mdharness validate
mdharness validate --source ./my-harness/source
```

---

### `mdharness rules search`

Search rules by criteria.

#### Options

| Option          | Short | Description                                              |
|-----------------|-------|----------------------------------------------------------|
| `--id`          |       | Filter by rule ID (exact or prefix, e.g. `SEC` or `SEC-003`) |
| `--title`       |       | Search in rule titles (substring, case-insensitive)      |
| `--level`       |       | Filter by level (`MUST` or `SHOULD`)                     |
| `--languages`   | `-l`  | Filter by applicable languages                           |
| `--frameworks`  | `-f`  | Filter by applicable frameworks                          |
| `--types`       | `-T`  | Filter by applicable types                               |
| `--category`    | `-c`  | Filter by category (e.g. `security`, `testing`)          |
| `--waivable`    |       | Filter by waivable status (`true` or `false`)            |
| `--owner`       |       | Filter by owning team (substring, case-insensitive)      |
| `--format`      |       | Output format: `table` (default), `json`, `yaml`, `ids`  |

#### Examples

```bash
# Find all MUST-level security rules
mdharness rules search --category security --level MUST

# Find rules that apply to Java Spring APIs
mdharness rules search --languages java --frameworks spring --types api

# Find non-waivable rules
mdharness rules search --waivable false

# Output as JSON for scripting
mdharness rules search --level MUST --format json

# Search by title keyword
mdharness rules search --title "logging"
```

---

### `mdharness rules count`

Count rules matching criteria. Accepts the same filter options as `rules search`.

#### Options

| Option       | Description                                              |
|--------------|----------------------------------------------------------|
| `--group-by` | Group counts by: `category`, `level`, `language`, `framework`, `type`, `owner` |

#### Examples

```bash
# Total rule count
mdharness rules count

# Count by category
mdharness rules count --group-by category

# Count MUST rules per category
mdharness rules count --level MUST --group-by category

# Count rules applicable to Python
mdharness rules count --languages python
```

---

### `mdharness rules show`

Display the full details of a single rule by ID.

#### Examples

```bash
mdharness rules show SEC-003
```

---

### `mdharness adr list`

List all ADRs with their ID, title, status, and date.

#### Options

| Option          | Short | Description                                              |
|-----------------|-------|----------------------------------------------------------|
| `--status`      |       | Filter by status (e.g. `Accepted`, `Deprecated`)         |
| `--languages`   | `-l`  | Filter by applicable languages                           |
| `--frameworks`  | `-f`  | Filter by applicable frameworks                          |
| `--types`       | `-T`  | Filter by applicable types                               |
| `--format`      |       | Output format: `table` (default), `json`, `yaml`         |

#### Examples

```bash
mdharness adr list
mdharness adr list --status Accepted
```

---

### `mdharness adr show`

Display the full details of a single ADR by ID.

#### Examples

```bash
mdharness adr show 0001
```

---

## Exit Codes

| Code | Meaning                     |
|------|-----------------------------|
| 0    | Success                     |
| 1    | Validation errors           |
| 2    | Invalid arguments / usage   |
