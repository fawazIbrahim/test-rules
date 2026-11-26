# Validation Rules

Constraints the generator must enforce when processing source YAML files.

## ADR Validation

1. **Unique IDs**: no two ADR records may share the same `id`.
2. **Unique codes**: no two ADR records may share the same `code`.
3. **ID format**: must be a zero-padded 4-digit string (`0001`-`9999`).
4. **Code format**: lowercase alphanumeric with hyphens or underscores only. No spaces.
5. **Date format**: must be a valid ISO 8601 date (`YYYY-MM-DD`).
6. **Status values**: must be one of a known set (e.g. `Proposed`, `Accepted`, `Deprecated`, `Superseded`).
7. **Rules-concerned references**: each referenced rule ID should exist in the rules catalog. Warn if not found.
8. **applied-to structure**: must contain `languages`, `frameworks`, and `types`, each as a list with at least one entry.
9. **applied-to values**: same validation as rules — languages, frameworks, and types must be from the allowed lists; `ALL` cannot appear alongside other values.
10. **Required fields**: all fields listed as required must be present and non-empty.

## Rules Validation

1. **Unique IDs**: no two rules across the entire catalog may share the same `id`.
2. **ID format**: must match `<PREFIX>-<NNNN>` where prefix matches the category and NNNN is zero-padded.
3. **Prefix consistency**: a rule's prefix must match the file it lives in (e.g. `SEC-*` rules in `security-rules.yaml`).
4. **Level values**: must be `MUST` or `SHOULD`.
5. **Waivable default**: if omitted, defaults to `true`.
6. **applied-to structure**: must contain `languages`, `frameworks`, and `types`, each as a list with at least one entry.
7. **languages values**: each entry must be one of `java`, `kotlin`, `typescript`, `javascript`, `python`, `go`, `csharp`, `ALL`. `ALL` cannot appear alongside other values.
8. **frameworks values**: each entry must be one of `spring`, `quarkus`, `node`, `nestjs`, `express`, `angular`, `react`, `vue`, `fastapi`, `django`, `dotnet`, `ALL`. `ALL` cannot appear alongside other values.
9. **types values**: each entry must be one of `api`, `batch`, `worker`, `spa`, `ssr`, `mobile`, `library`, `cli`, `function`, `iac`, `ALL`. `ALL` cannot appear alongside other values.
10. **Required fields**: all fields listed as required must be present and non-empty.

## Generator Behavior on Validation Failure

- **Error**: stop generation and report the issue with file, line/record reference, and reason.
- **Warning**: continue generation but report the issue (e.g. a rules-concerned reference to a non-existent rule).
