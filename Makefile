.PHONY: validate test lint typecheck manifest manifest-update check

validate:
	PYTHONPATH=src python -m gfjd.validate

test:
	PYTHONPATH=src python -m pytest

lint:
	python -m ruff check src tests

typecheck:
	PYTHONPATH=src python -m mypy src

manifest:
	PYTHONPATH=src python -m gfjd.validate --manifest

manifest-update:
	PYTHONPATH=src python -m gfjd.manifest

check: validate test lint typecheck manifest
