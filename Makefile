COMPOSE := docker compose

.PHONY: distclean integration-test-backend lint setup test-backend test-frontend unit-test-backend unit-test-frontend

distclean:
	$(COMPOSE) down --volumes

integration-test-backend:
	$(COMPOSE) run --rm backend pytest tests/integration

lint:
	pre-commit run --all-files --show-diff-on-failure

setup:
	git config blame.ignoreRevsFile .git-blame-ignore-revs
	pre-commit install

test-backend: unit-test-backend integration-test-backend

test-frontend: unit-test-frontend

unit-test-backend:
	$(COMPOSE) run --rm --no-deps backend pytest tests/unit

unit-test-frontend:
	$(COMPOSE) run --rm --no-deps frontend yarn test:ci
