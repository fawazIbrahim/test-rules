"""Shared fixtures for mdharness tests."""

import os
import pytest
import yaml


@pytest.fixture
def tmp_source(tmp_path):
    """Create a temporary source directory with valid sample data."""
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    catalog_dir = source_dir / "rules-catalog"
    catalog_dir.mkdir()

    adr_data = {
        "records": [
            {
                "id": "0001",
                "code": "use-postgresql",
                "title": "Use PostgreSQL as primary database",
                "status": "Accepted",
                "date": "2024-01-15",
                "decider": "Platform Team",
                "rules-concerned": ["DATA-0001"],
                "applied-to": {
                    "languages": ["ALL"],
                    "frameworks": ["ALL"],
                    "types": ["api", "worker"],
                },
                "context": "We need a relational database.",
                "decision": "Use PostgreSQL.",
                "consequences": "Teams must use PostgreSQL.",
            },
            {
                "id": "0002",
                "code": "adopt-react",
                "title": "Adopt React for frontend",
                "status": "Accepted",
                "date": "2024-02-01",
                "decider": "Frontend Guild",
                "rules-concerned": [],
                "applied-to": {
                    "languages": ["typescript", "javascript"],
                    "frameworks": ["react"],
                    "types": ["spa", "ssr"],
                },
                "context": "Need a frontend framework.",
                "decision": "Adopt React.",
                "consequences": "New SPAs use React.",
            },
        ]
    }
    with open(source_dir / "adr.yaml", "w") as f:
        yaml.dump(adr_data, f, default_flow_style=False, sort_keys=False)

    security_rules = {
        "rules": [
            {
                "id": "SEC-0001",
                "title": "Validate all user input",
                "level": "MUST",
                "owner": "Security Team",
                "applied-to": {
                    "languages": ["ALL"],
                    "frameworks": ["ALL"],
                    "types": ["ALL"],
                },
                "waivable": False,
                "since": "0.1.0",
                "description": "All user input must be validated.",
                "content": "Validate at the boundary.",
            },
            {
                "id": "SEC-0002",
                "title": "Use parameterized queries",
                "level": "MUST",
                "owner": "Security Team",
                "applied-to": {
                    "languages": ["java", "python"],
                    "frameworks": ["spring", "fastapi"],
                    "types": ["api"],
                },
                "since": "0.1.0",
                "description": "Prevent SQL injection.",
                "content": "Use parameterized queries for all DB access.",
            },
        ]
    }
    with open(catalog_dir / "security-rules.yaml", "w") as f:
        yaml.dump(security_rules, f, default_flow_style=False, sort_keys=False)

    testing_rules = {
        "rules": [
            {
                "id": "TEST-0001",
                "title": "Unit test coverage minimum",
                "level": "SHOULD",
                "owner": "QA Guild",
                "applied-to": {
                    "languages": ["ALL"],
                    "frameworks": ["ALL"],
                    "types": ["ALL"],
                },
                "since": "0.1.0",
                "description": "Maintain minimum 80% coverage.",
                "content": "All modules should have unit tests.",
            },
        ]
    }
    with open(catalog_dir / "testing-rules.yaml", "w") as f:
        yaml.dump(testing_rules, f, default_flow_style=False, sort_keys=False)

    data_rules = {
        "rules": [
            {
                "id": "DATA-0001",
                "title": "Use migrations for schema changes",
                "level": "MUST",
                "owner": "Platform Team",
                "applied-to": {
                    "languages": ["ALL"],
                    "frameworks": ["ALL"],
                    "types": ["api", "worker"],
                },
                "since": "0.1.0",
                "description": "Schema changes require migrations.",
                "content": "Always use migration scripts.",
            },
        ]
    }
    with open(catalog_dir / "data-persistence-rules.yaml", "w") as f:
        yaml.dump(data_rules, f, default_flow_style=False, sort_keys=False)

    return str(source_dir)


@pytest.fixture
def tmp_target(tmp_path):
    """Return a temporary target directory path."""
    target_dir = tmp_path / "target"
    return str(target_dir)
