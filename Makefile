.PHONY: install lint format-check typecheck test test-cov test-integration-real

install:
	uv sync --group dev

lint:
	uv run ruff check .

format-check:
	uv run ruff format --check .

typecheck:
	uv run ty check custom_components/stewart_filmscreen

test:
	uv run pytest

test-cov:
	uv run pytest

test-integration-real:
	@echo "Running read-only real-device integration tests against $${STEWART_HOST:-unset}:$${STEWART_PORT:-23}"
	@test -n "$${STEWART_HOST:-}" || (echo "Set STEWART_HOST to your CVM host/IP" && exit 1)
	@STEWART_ITEST=1 uv run pytest -v -m integration_real
