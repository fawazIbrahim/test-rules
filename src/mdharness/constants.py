"""Allowed values and category definitions used across the harness."""

# Valid programming languages a rule or ADR can target. "ALL" means every language.
ALLOWED_LANGUAGES = [
    "java", "kotlin", "typescript", "javascript", "python", "go", "csharp", "ALL",
]

# Valid frameworks a rule or ADR can target. "ALL" means every framework.
ALLOWED_FRAMEWORKS = [
    "spring", "quarkus", "node", "nestjs", "express",
    "angular", "react", "vue", "fastapi", "django", "dotnet", "ALL",
]

# Valid application types a rule or ADR can target. "ALL" means every type.
ALLOWED_TYPES = [
    "api", "batch", "worker", "spa", "ssr", "mobile",
    "library", "cli", "function", "iac", "ALL",
]

# The lifecycle statuses an ADR can have.
ALLOWED_ADR_STATUSES = ["Proposed", "Accepted", "Deprecated", "Superseded"]

# How strictly a rule must be followed: MUST = mandatory, SHOULD = recommended.
ALLOWED_LEVELS = ["MUST", "SHOULD"]

# Maps YAML filename stem (without '-rules.yaml') to (prefix, human-readable name).
# Example: "common" -> ("CMN", "Common") means common-rules.yaml uses prefix CMN.
CATEGORY_MAP = {
    "common":                   ("CMN",        "Common"),
    "commands":                 ("CMD",        "Commands"),
    "project-structure":        ("PRJ-STRUCT", "Project Structure"),
    "conventions":              ("CONV",       "Conventions"),
    "dependencies":             ("DEPS",       "Dependencies"),
    "architecture":             ("ARCH",       "Architecture"),
    "data-persistence":         ("DATA",       "Data & Persistence"),
    "interfaces-contracts":     ("INTF",       "Interfaces & Contracts"),
    "error-handling":           ("ERR",        "Error Handling"),
    "observability":            ("OBS",        "Observability"),
    "security":                 ("SEC",        "Security"),
    "configuration":            ("CFG",        "Configuration"),
    "testing":                  ("TEST",       "Testing"),
    "performance-concurrency":  ("PERF",       "Performance & Concurrency"),
    "workflow":                 ("WF",         "Workflow"),
}
