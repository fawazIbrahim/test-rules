# ADR Specification

## Source Format

File: `source/adr.yaml`

```yaml
records:
  - id: 0001
    code: <code-title-in-snake-case>
    title: <Human readable title>
    status: <Status>
    date: <YYYY-MM-DD>
    decider: <Decider>
    rules-concerned: <List of rule IDs or empty list []>
    applied-to:
      languages: [<list of languages, or ALL>]
      frameworks: [<list of frameworks, or ALL>]
      types: [<list of types, or ALL>]
    context: |
      <The context>
    decision: |
      <The decision>
    consequences: |
      <The consequences>
```

### Field Definitions

| Field             | Type       | Required | Description                                      |
|-------------------|------------|----------|--------------------------------------------------|
| `id`              | string     | yes      | Zero-padded 4-digit number (e.g. `0001`)         |
| `code`            | string     | yes      | Snake-case slug used in the filename              |
| `title`           | string     | yes      | Human-readable title                              |
| `status`          | string     | yes      | ADR status (e.g. Accepted, Superseded, Deprecated)|
| `date`            | date       | yes      | ISO 8601 date                                     |
| `decider`         | string     | yes      | Person or team who made the decision              |
| `rules-concerned` | list       | yes      | Rule IDs affected by this ADR, or `[]`            |
| `applied-to.languages`  | list | yes      | Applicable languages; `[ALL]` for universal       |
| `applied-to.frameworks` | list | yes      | Applicable frameworks/runtimes; `[ALL]` for universal |
| `applied-to.types`      | list | yes      | Applicable project types; `[ALL]` for universal   |
| `context`         | multiline  | yes      | Background and problem statement                  |
| `decision`        | multiline  | yes      | What was decided                                  |
| `consequences`    | multiline  | yes      | Expected impact                                   |

## Output Format

Directory: `target/adr/`

Filename pattern: `adr-<id>-<code>.md` (e.g. `adr-0001-use-postgresql.md`)

### Template

```markdown
# <id>. <title>
---
status: <status>
date: <date>
decider: <decider>
rules-concerned: <rules-concerned>
---

## Context
<context>

## Decision
<decision>

## Consequences
<consequences>
```

## Generation Rules

1. One ADR record produces exactly one Markdown file.
2. The `id` field is used as-is (zero-padded) in both the heading and the filename.
3. The `code` field is used as-is in the filename; it must be valid for filesystem paths (lowercase, hyphens or underscores, no spaces).
4. Multiline fields (`context`, `decision`, `consequences`) are rendered as-is, preserving line breaks.
5. `rules-concerned` is rendered as a YAML-style list inline (e.g. `[SEC-001, DEPS-003]`) or `[]`.
6. `applied-to` uses the same three-dimension semantics as rules (AND between dimensions, OR within). See [03-rules-spec.md](03-rules-spec.md).
