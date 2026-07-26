.PHONY: help install validate validate-strict test coverage compile generated status graph release-rehearsal check clean

PYTHON ?= python
SOURCE_DATE_EPOCH ?= 1784419200

help:
	@echo "install            Install editable package with development tools"
	@echo "validate           Validate schemas, data, programme and evidence"
	@echo "validate-strict    Treat validation warnings as failures"
	@echo "test               Run unit and integration tests"
	@echo "coverage           Run tests with branch coverage"
	@echo "generated          Verify generated conductor status is current"
	@echo "status             Regenerate conductor status"
	@echo "release-rehearsal  Build and verify a deterministic 0.x release"
	@echo "check              Run the required local/CI quality gate"

install:
	$(PYTHON) -m pip install -e '.[dev]'

validate:
	PYTHONPATH=src $(PYTHON) -m gfjd validate

validate-strict:
	PYTHONPATH=src $(PYTHON) -m gfjd validate --strict

compile:
	$(PYTHON) -m compileall -q src tests

test:
	PYTHONPATH=src $(PYTHON) -m pytest -q

coverage:
	PYTHONPATH=src $(PYTHON) -m pytest --cov=gfjd --cov-report=term-missing --cov-branch

generated:
	PYTHONPATH=src $(PYTHON) -m gfjd conductor check-generated

status:
	PYTHONPATH=src $(PYTHON) -m gfjd conductor status --write docs/programme/generated/status.md
	PYTHONPATH=src $(PYTHON) -m gfjd conductor graph --write docs/programme/generated/programme-graph.mmd

release-rehearsal:
	rm -rf build/rehearsal
	SOURCE_DATE_EPOCH=$(SOURCE_DATE_EPOCH) PYTHONPATH=src $(PYTHON) -m gfjd release build --version 0.3.0-rehearsal --output build/rehearsal --source-date-epoch $(SOURCE_DATE_EPOCH) --allow-version-override
	PYTHONPATH=src $(PYTHON) -m gfjd release verify build/rehearsal/gfjd-0.3.0-rehearsal

check: compile validate test generated release-rehearsal

clean:
	rm -rf build dist .coverage .pytest_cache
	find src tests -type d -name __pycache__ -prune -exec rm -rf {} +
