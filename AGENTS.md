# AGENTS.md

## Project

**mdharness** — A Python CLI that generates filtered Markdown (ADRs + rules) from YAML sources for coding agents.

## Mode: Spec-Driven Development

All specs live in `specs/`. They are the single source of truth for what to build. Code implements specs; it does not invent behavior.

## Workflow

1. **Orient** — Read `specs/` and any existing source code to understand current state.
2. **Check alignment** — Before writing code, confirm the relevant spec covers the behavior. If it doesn't, update the spec first and get user approval.
3. **Implement** — Write code that matches the spec exactly. No undocumented features, no silent deviations.
4. **Validate** — Run tests. Every spec requirement should have a corresponding test.
5. **Report** — Summarize what was done and what's next.

## Rules

- **Beginner-friendly code** — Write code that a Python beginner can read and understand. Prefer explicit over clever. Specifically:
  - Use plain `for` loops and `if/else` over complex comprehensions or chained expressions.
  - One thing per line — avoid nesting multiple operations in a single statement.
  - Use simple standard-library types (`dict`, `list`, `str`) over advanced constructs (dataclasses are fine, metaclasses are not).
  - Name variables and functions descriptively — `matched_rules` not `res`, `is_valid` not `v`.
  - No decorators beyond the basics (`@staticmethod`, `@property`, framework-required ones like `@click.command()`).
  - No `*args`/`**kwargs` unless a framework requires it. Spell out parameters explicitly.
  - Keep functions short and single-purpose. If a function needs a scroll, split it.
  - Add a one-line docstring to each public function explaining what it does in plain language.
- **Spec gaps** — If a spec is ambiguous or missing detail needed to implement, ask the user or propose a spec update. Do not guess.
- **Spec changes** — When the user requests behavior that conflicts with a spec, update the spec first, then the code.
- **No gold-plating** — Implement what the spec says. Nothing more.
- **Test coverage** — Every command, validation rule, and generation rule in the specs must have tests. Line and branch coverage must be at least 80%.
- **File structure** — Respect the directory layout defined in `specs/01-overview.md`.
