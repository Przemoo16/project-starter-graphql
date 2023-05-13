COMPOSE := docker compose

.PHONY: setup test-backend test-frontend

setup:
	git config blame.ignoreRevsFile .git-blame-ignore-revs
	pre-commit install

test-backend:
	$(COMPOSE) run --rm --no-deps backend pytest .

test-frontend:
	$(COMPOSE) run --rm --no-deps frontend yarn test:ci
