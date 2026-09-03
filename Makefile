.PHONY: help install validate validate-strict test test-focused test-timed unit unit-parallel property integration coverage compile format lint typecheck contracts policy security generated status graph release-rehearsal integration-rehearsals package-reproducibility release-reproducibility bootstrap-preflight bootstrap-plan autonomy-context autonomy-fast autonomy-full check clean

PYTHON ?= python
SOURCE_DATE_EPOCH ?= 1786752000
REHEARSAL_VERSION ?= 0.6.0-alpha.2-rehearsal
PYTEST_ARGS ?=
FOCUSED_TESTS ?=
LOCAL_TEST_TIMINGS ?= build/test-timings-local.json

help:
	@echo "install                  Install locked development environment"
	@echo "validate                 Validate schemas, data, programme and evidence"
	@echo "test                     Run complete deterministic suite"
	@echo "test-focused             Run FOCUSED_TESTS during iteration"
	@echo "test-timed               Run the complete suite and retain timings"
	@echo "unit-parallel            Run the fast unit tier with two file-grouped workers"
	@echo "coverage                 Run branch coverage and enforce budgets"
	@echo "contracts                Verify public-contract lock"
	@echo "policy                   Audit workflow and repository-control policy"
	@echo "integration-rehearsals   Exercise data, evidence, warehouse, backup and release paths"
	@echo "package-reproducibility  Build two wheels and require byte identity"
	@echo "release-reproducibility  Build two release archives and require byte identity"
	@echo "autonomy-context        Build and verify the deterministic agent resume packet"
	@echo "autonomy-fast           Fast fail-closed autonomous iteration gate"
	@echo "autonomy-full           Maximal autonomous checkpoint harness"
	@echo "check                    Run the required local/CI quality gate"

install:
	uv sync --frozen --all-extras

validate:
	PYTHONPATH=src $(PYTHON) -m gfjd validate

validate-strict:
	PYTHONPATH=src $(PYTHON) -m gfjd validate --strict

compile:
	$(PYTHON) -m compileall -q src tests scripts

format:
	$(PYTHON) -m ruff format --check src tests scripts

lint:
	$(PYTHON) -m ruff check src tests scripts

typecheck:
	$(PYTHON) -m mypy src

test:
	mkdir -p $(dir $(LOCAL_TEST_TIMINGS))
	GFJD_TEST_TIMINGS=$(LOCAL_TEST_TIMINGS) PYTHONPATH=src $(PYTHON) -m pytest -q $(PYTEST_ARGS)

test-focused:
	@test -n "$(strip $(FOCUSED_TESTS))" || { echo "Set FOCUSED_TESTS to one or more test paths or node IDs" >&2; exit 2; }
	PYTHONPATH=src $(PYTHON) -m pytest -q $(FOCUSED_TESTS) $(PYTEST_ARGS)

test-timed: test

unit:
	PYTHONPATH=src $(PYTHON) -m pytest -q -m "unit and not slow" $(PYTEST_ARGS)

unit-parallel:
	PYTHONPATH=src $(PYTHON) -m pytest -q -n 2 --dist loadfile -m "unit and not slow" $(PYTEST_ARGS)

property:
	PYTHONPATH=src $(PYTHON) -m pytest -q -m "property and not slow" $(PYTEST_ARGS)

integration:
	PYTHONPATH=src $(PYTHON) -m pytest -q -m "integration and not slow" $(PYTEST_ARGS)

coverage:
	rm -f .coverage build/coverage.json
	mkdir -p build
	PYTHONPATH=src $(PYTHON) -m pytest -q -m "not slow" --cov=gfjd --cov-branch --cov-report=term-missing --cov-report=json:build/coverage.json
	PYTHONPATH=src $(PYTHON) -m gfjd harness coverage build/coverage.json

contracts:
	PYTHONPATH=src $(PYTHON) -m gfjd harness contracts
	PYTHONPATH=src $(PYTHON) scripts/verify_shared_medallion_contracts.py --verify data/federation/shared-medallion-contracts-2026-09-03/report.json

policy:
	PYTHONPATH=src $(PYTHON) -m gfjd policy ci
	PYTHONPATH=src $(PYTHON) -m gfjd policy repository
	PYTHONPATH=src $(PYTHON) -m gfjd harness lock

security:
	mkdir -p build
	uv export --frozen --all-extras --format requirements-txt --no-emit-project --output-file build/pip-audit-requirements.txt
	uv run pip-audit --strict -r build/pip-audit-requirements.txt --progress-spinner off --format json --output build/pip-audit.json
	uv run bandit -r src/gfjd -ll -f json -o build/bandit.json
	uv run zizmor --offline --pedantic --min-severity medium --format sarif .github > build/zizmor.sarif
	$(PYTHON) -c 'import hashlib,pathlib; files=[pathlib.Path("build/pip-audit.json"),pathlib.Path("build/bandit.json"),pathlib.Path("build/zizmor.sarif")]; pathlib.Path("build/security-receipts.sha256").write_text("".join(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p}\n" for p in files), encoding="utf-8")'

generated:
	PYTHONPATH=src $(PYTHON) -m gfjd conductor check-generated

status:
	PYTHONPATH=src $(PYTHON) -m gfjd conductor status --write docs/programme/generated/status.md
	PYTHONPATH=src $(PYTHON) -m gfjd conductor graph --write docs/programme/generated/programme-graph.mmd

release-rehearsal:
	rm -rf build/rehearsal
	SOURCE_DATE_EPOCH=$(SOURCE_DATE_EPOCH) PYTHONPATH=src $(PYTHON) -m gfjd release build --version $(REHEARSAL_VERSION) --output build/rehearsal --source-date-epoch $(SOURCE_DATE_EPOCH) --allow-version-override
	PYTHONPATH=src $(PYTHON) -m gfjd release verify build/rehearsal/gfjd-$(REHEARSAL_VERSION)

integration-rehearsals: federation-bundle-rehearsal
	rm -rf build/demo build/evidence build/comparability build/census build/warehouse build/backup build/restore-rehearsal build/bootstrap-rehearsal build/governance build/gate-packs
	PYTHONPATH=src $(PYTHON) -m gfjd demo run --output build/demo
	PYTHONPATH=src $(PYTHON) -m gfjd demo verify --output build/demo
	PYTHONPATH=src $(PYTHON) -m gfjd evidence build --output build/evidence --as-of 2026-07-27
	PYTHONPATH=src $(PYTHON) -m gfjd evidence verify --output build/evidence
	PYTHONPATH=src $(PYTHON) -m gfjd comparability build --input 'build/demo/gold/*.csv' --output build/comparability
	PYTHONPATH=src $(PYTHON) -m gfjd comparability verify --output build/comparability
	PYTHONPATH=src $(PYTHON) -m gfjd census build --output build/census
	PYTHONPATH=src $(PYTHON) -m gfjd census verify --output build/census
	PYTHONPATH=src $(PYTHON) -m gfjd research-pack AUS --output build/research-packs
	PYTHONPATH=src $(PYTHON) -m gfjd warehouse build --output build/warehouse/gfjd.sqlite --source-date-epoch $(SOURCE_DATE_EPOCH)
	PYTHONPATH=src $(PYTHON) -m gfjd warehouse verify build/warehouse/gfjd.sqlite
	PYTHONPATH=src $(PYTHON) -m gfjd resilience backup --output build/backup --source-date-epoch $(SOURCE_DATE_EPOCH)
	PYTHONPATH=src $(PYTHON) -m gfjd resilience verify build/backup/gfjd-critical-state.zip
	PYTHONPATH=src $(PYTHON) -m gfjd resilience restore-rehearsal build/backup/gfjd-critical-state.zip --output build/restore-rehearsal
	PYTHONPATH=src $(PYTHON) -m gfjd resilience verify-restore build/restore-rehearsal/restore-receipt.json
	PYTHONPATH=src $(PYTHON) -m gfjd bootstrap plan --scan-root .. --output build/bootstrap-rehearsal
	PYTHONPATH=src $(PYTHON) -m gfjd governance build --output build/governance --as-of 2026-07-27
	PYTHONPATH=src $(PYTHON) -m gfjd governance verify --output build/governance
	$(MAKE) release-rehearsal

package-reproducibility:
	rm -rf build/wheel-first build/wheel-second
	mkdir -p build/wheel-first build/wheel-second
	SOURCE_DATE_EPOCH=$(SOURCE_DATE_EPOCH) $(PYTHON) scripts/build_distribution.py --wheel --sdist --outdir build/wheel-first
	SOURCE_DATE_EPOCH=$(SOURCE_DATE_EPOCH) $(PYTHON) scripts/build_distribution.py --wheel --sdist --outdir build/wheel-second
	PYTHONPATH=src $(PYTHON) -m gfjd harness wheel $$(find build/wheel-first -name '*.whl' -print -quit)
	PYTHONPATH=src $(PYTHON) -m gfjd harness wheel $$(find build/wheel-second -name '*.whl' -print -quit)
	PYTHONPATH=src $(PYTHON) -m gfjd harness sdist $$(find build/wheel-first -name '*.tar.gz' -print -quit)
	PYTHONPATH=src $(PYTHON) -m gfjd harness sdist $$(find build/wheel-second -name '*.tar.gz' -print -quit)
	PYTHONPATH=src $(PYTHON) -m gfjd harness repro $$(find build/wheel-first -name '*.whl' -print -quit) $$(find build/wheel-second -name '*.whl' -print -quit)
	PYTHONPATH=src $(PYTHON) -m gfjd harness repro $$(find build/wheel-first -name '*.tar.gz' -print -quit) $$(find build/wheel-second -name '*.tar.gz' -print -quit)

release-reproducibility:
	rm -rf build/repro-first build/repro-second
	SOURCE_DATE_EPOCH=$(SOURCE_DATE_EPOCH) PYTHONPATH=src $(PYTHON) -m gfjd release build --version $(REHEARSAL_VERSION) --output build/repro-first --source-date-epoch $(SOURCE_DATE_EPOCH) --allow-version-override
	SOURCE_DATE_EPOCH=$(SOURCE_DATE_EPOCH) PYTHONPATH=src $(PYTHON) -m gfjd release build --version $(REHEARSAL_VERSION) --output build/repro-second --source-date-epoch $(SOURCE_DATE_EPOCH) --allow-version-override
	PYTHONPATH=src $(PYTHON) -m gfjd release verify build/repro-first/gfjd-$(REHEARSAL_VERSION)
	PYTHONPATH=src $(PYTHON) -m gfjd release verify build/repro-second/gfjd-$(REHEARSAL_VERSION)
	PYTHONPATH=src $(PYTHON) -m gfjd harness repro build/repro-first/gfjd-$(REHEARSAL_VERSION).zip build/repro-second/gfjd-$(REHEARSAL_VERSION).zip

bootstrap-preflight:
	PYTHONPATH=src $(PYTHON) -m gfjd bootstrap preflight

bootstrap-plan:
	PYTHONPATH=src $(PYTHON) -m gfjd bootstrap plan --scan-root .. --output build/bootstrap

autonomy-context:
	PYTHONPATH=src $(PYTHON) -m gfjd autonomy context --output build/autonomy
	PYTHONPATH=src $(PYTHON) -m gfjd autonomy verify --output build/autonomy

autonomy-fast: compile contracts validate-strict unit generated policy autonomy-context

.PHONY: medallion-lineage-rehearsal
medallion-lineage-rehearsal:
	PYTHONPATH=src $(PYTHON) scripts/rehearse_medallion_lineage.py --output build/medallion-lineage/rehearsal.json
	PYTHONPATH=src $(PYTHON) scripts/rehearse_medallion_lineage.py --verify build/medallion-lineage/rehearsal.json

.PHONY: federation-bundle-rehearsal
federation-bundle-rehearsal:
	PYTHONPATH=src $(PYTHON) scripts/rehearse_federation_bundle.py --output-directory build/federation-rehearsal
	PYTHONPATH=src $(PYTHON) scripts/rehearse_federation_bundle.py --verify-directory build/federation-rehearsal

autonomy-full: format lint typecheck coverage check integration-rehearsals medallion-lineage-rehearsal federation-bundle-rehearsal package-reproducibility release-reproducibility autonomy-context

check: compile contracts validate test generated policy release-rehearsal

clean:
	rm -rf build dist .coverage .pytest_cache .mypy_cache .ruff_cache
	find src tests scripts -type d -name __pycache__ -prune -exec rm -rf {} +
