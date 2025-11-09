.PHONY: install dev build test

install:
	cd ui && npm install
	cd api && uv add

dev:
	docker compose up --build

build-ui:
	cd ui && npm run build

build-api:
	cd api && uv run python -m build

test-ui:
	cd ui && npm test

test-api:
	cd api && uv run pytest
