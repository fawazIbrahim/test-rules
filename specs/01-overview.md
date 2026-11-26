# MD Harness Generator - Overview

## Purpose

A tool that generates Markdown files (ADRs and rules) from YAML source files, targeting coding agents. The harness maintains a single source of truth in YAML and produces human-readable, consistently formatted Markdown output.

## High-Level Flow

```
source/                          target/
  adr.yaml          -->            docs/adr/
  rules-catalog/                   rules/
    common-rules.yaml    -->         common.md
    <category>.yaml      -->         <category>.md
```

## Directory Layout

```
<project-root>/
  source/
    adr.yaml
    rules-catalog/
      common-rules.yaml
      commands-rules.yaml
      project-structure-rules.yaml
      conventions-rules.yaml
      dependencies-rules.yaml
      architecture-rules.yaml
      data-persistence-rules.yaml
      interfaces-contracts-rules.yaml
      error-handling-rules.yaml
      observability-rules.yaml
      security-rules.yaml
      configuration-rules.yaml
      testing-rules.yaml
      performance-concurrency-rules.yaml
      workflow-rules.yaml
  target/
    adr/
      adr-0001-<code-title>.md
      adr-0002-<code-title>.md
    rules/
      common.md
      commands.md
      project-structure.md
      conventions.md
      dependencies.md
      architecture.md
      data-persistence.md
      interfaces-contracts.md
      error-handling.md
      observability.md
      security.md
      configuration.md
      testing.md
      performance-concurrency.md
      workflow.md
```
