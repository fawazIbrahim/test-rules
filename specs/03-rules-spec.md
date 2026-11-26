# Rules Specification

## Source Format

Directory: `source/rules-catalog/`

Each category has its own YAML file. `common-rules.yaml` holds rules shared across all categories.

```yaml
rules:
  - id: <PREFIX>-<NNNN>
    title: <Human readable title>
    level: <MUST | SHOULD>
    owner: <Team that approves changes and waivers>
    applied-to:
      languages: [<list of languages, or ALL>]
      frameworks: [<list of frameworks, or ALL>]
      types: [<list of types, or ALL>]
    waivable: <true | false>
    since: <Harness version>
    description: <Short description>
    content: |
      <Detailed rule content>
```

### Field Definitions

| Field                  | Type     | Required | Default | Description                                        |
|------------------------|----------|----------|---------|----------------------------------------------------|
| `id`                   | string   | yes      | -       | Category prefix + zero-padded number (e.g. `SEC-003`) |
| `title`                | string   | yes      | -       | Human-readable title                                |
| `level`                | enum     | yes      | -       | `MUST` or `SHOULD`                                  |
| `owner`                | string   | yes      | -       | Team that approves changes and waivers              |
| `applied-to.languages`  | list     | yes      | -       | Applicable languages; `[ALL]` for universal         |
| `applied-to.frameworks` | list     | yes      | -       | Applicable frameworks/runtimes; `[ALL]` for universal |
| `applied-to.types`      | list     | yes      | -       | Applicable project types; `[ALL]` for universal     |
| `waivable`             | boolean  | no       | `true`  | Whether an ADR can waive this rule                  |
| `since`                | string   | yes      | -       | Harness version that introduced the rule            |
| `description`          | string   | yes      | -       | Short description                                   |
| `content`              | multiline| yes      | -       | Full rule body                                      |

### applied-to Semantics

- **Between** `languages`, `frameworks`, and `types`: AND (all three must match)
- **Within** each dimension: OR (any one match suffices)
- `ALL` means the rule applies regardless of that dimension

### Allowed `languages` Values

`java`, `kotlin`, `typescript`, `javascript`, `python`, `go`, `csharp`, `ALL`.

### Allowed `frameworks` Values

`spring`, `quarkus`, `node`, `nestjs`, `express`, `angular`, `react`, `vue`, `fastapi`, `django`, `dotnet`, `ALL`.

### Allowed `types` Values

`api`, `batch`, `worker`, `spa`, `ssr`, `mobile`, `library`, `cli`, `function`, `iac`, `ALL`.

See [06-application-types.md](06-application-types.md) and [07-stacks.md](07-stacks.md) for definitions.

## Categories and ID Prefixes

| #  | Category                  | YAML File                            | ID Prefix   |
|----|---------------------------|--------------------------------------|-------------|
| -  | Common                    | `common-rules.yaml`                  | CMN         |
| 1  | Commands                  | `commands-rules.yaml`                | CMD         |
| 2  | Project structure         | `project-structure-rules.yaml`       | PRJ-STRUCT  |
| 3  | Conventions               | `conventions-rules.yaml`             | CONV        |
| 4  | Dependencies              | `dependencies-rules.yaml`            | DEPS        |
| 5  | Architecture              | `architecture-rules.yaml`            | ARCH        |
| 6  | Data & persistence        | `data-persistence-rules.yaml`        | DATA        |
| 7  | Interfaces & contracts    | `interfaces-contracts-rules.yaml`    | INTF        |
| 8  | Error handling            | `error-handling-rules.yaml`          | ERR         |
| 9  | Observability             | `observability-rules.yaml`           | OBS         |
| 10 | Security                  | `security-rules.yaml`                | SEC         |
| 11 | Configuration             | `configuration-rules.yaml`           | CFG         |
| 12 | Testing                   | `testing-rules.yaml`                 | TEST        |
| 13 | Performance & concurrency | `performance-concurrency-rules.yaml` | PERF        |
| 14 | Workflow                  | `workflow-rules.yaml`                | WF          |

## Output Format

Directory: `target/rules/`

One output file per source YAML: `common-rules.yaml` -> `common.md`, `security-rules.yaml` -> `security.md`, etc.

### Template

```markdown
# Rules of <Type or Stack, e.g: Technical Stack: Java>

## <RULE-ID>. <title>
---
level: <level>
owner: <owner>
waivable: <waivable>
since: <since>
---

<description>

<content>
```

Rules within a file are rendered in the order they appear in the YAML source.

## Generation Rules

1. One YAML source file produces exactly one Markdown file.
2. The output file heading (`# Rules of ...`) uses the category's human-readable name.
3. Each rule is an H2 section (`## <id>. <title>`).
4. The YAML frontmatter block between `---` delimiters preserves the field order shown in the template.
5. `description` and `content` are separated by a blank line.
6. `waivable` defaults to `true` if omitted in the source YAML.
