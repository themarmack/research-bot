# Testing framework for the research-bot skills toolkit.
# See TESTING.md for the layered model. Deterministic layers (test, lint) are
# free and CI-safe; `evals` drives real agents and is LOCAL/scheduled only.

PYTHON ?= python3
VENV   ?= .venv
PIP    := $(VENV)/bin/pip
PY     := $(VENV)/bin/python

# Token-frugal evolve run flags (single cheap model, capped turns, no baseline).
EVOLVE_RUN_FLAGS ?= --no-tui --modified --failed

.PHONY: help setup test lint evals report gate check clean

help:
	@echo "make setup   - create venv + install prod & dev deps"
	@echo "make test    - deterministic unit + structural tests (pytest, no AI)"
	@echo "make lint    - evolve Tier-0 static checks (no AI)"
	@echo "make gate    - evolve report --check against committed results (no agents)"
	@echo "make check   - test + lint + gate (the CI gate; no agents, no key)"
	@echo "make evals   - LOCAL ONLY: run trigger/eval suites via the claude CLI"
	@echo "make report  - regenerate EVALUATION.md from committed results"

setup:
	$(PYTHON) -m venv $(VENV)
	$(PIP) install -q -r scripts/requirements.txt -r requirements-dev.txt

# Deterministic layers 0+1 — free, no AI, no credentials.
test:
	$(PY) -m pytest

# Layer 1 static skill/plugin checks (Tier 0). Needs the evolve binary on PATH.
lint:
	evolve run checks

# Gate CI on COMMITTED evidence — no agent runs, no API key.
gate:
	evolve report --check

report:
	evolve report

# Full local/CI gate. No agents.
check: test lint gate

# LOCAL ONLY — drives the claude CLI (subscription). Never run in CI.
evals:
	evolve run triggers $(EVOLVE_RUN_FLAGS)

clean:
	rm -rf $(VENV) .pytest_cache
	find . -name __pycache__ -type d -prune -exec rm -rf {} +
