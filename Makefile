.PHONY: install install-backend install-frontend \
        dev dev-backend dev-frontend \
        test test-backend test-frontend \
        lint lint-backend lint-frontend \
        typecheck typecheck-backend typecheck-frontend \
        e2e seed schemas clean

VENV := .venv
PY := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

install: install-backend install-frontend

install-backend:
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install --config-settings editable_mode=compat \
		-e packages/indic_text \
		-e packages/audio_metrics \
		-e packages/tts_runtime \
		-e "apps/api[dev]"

install-frontend:
	npm install --prefix apps/web

dev-backend:
	$(VENV)/bin/uvicorn app.main:app --reload --app-dir apps/api --port 8000

dev-frontend:
	npm run dev --prefix apps/web

dev:
	@echo "Run 'make dev-backend' and 'make dev-frontend' in separate terminals, or 'docker compose up'."

test-backend:
	$(PY) -m pytest -q packages/indic_text
	$(PY) -m pytest -q packages/audio_metrics
	$(PY) -m pytest -q packages/tts_runtime
	$(PY) -m pytest -q apps/api

test-frontend:
	npm run test --prefix apps/web

test: test-backend test-frontend

lint-backend:
	$(VENV)/bin/ruff check packages/indic_text packages/audio_metrics packages/tts_runtime apps/api

lint-frontend:
	npm run lint --prefix apps/web

lint: lint-backend lint-frontend

typecheck-backend:
	$(VENV)/bin/mypy packages/indic_text/indic_text packages/audio_metrics/audio_metrics packages/tts_runtime/tts_runtime apps/api/app

typecheck-frontend:
	npm run typecheck --prefix apps/web

typecheck: typecheck-backend typecheck-frontend

e2e:
	npm run e2e --prefix apps/web

seed:
	$(PY) scripts/seed_lexicon.py

schemas:
	$(PY) scripts/export_schemas.py

clean:
	rm -rf $(VENV) apps/web/node_modules apps/web/.next
