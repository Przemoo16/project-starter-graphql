COMPOSE := docker compose

.PHONY: build lint run setup test-backend test-frontend

build:
	$(COMPOSE) build

lint:
	pre-commit run --all-files --show-diff-on-failure

run:
	$(COMPOSE) up

setup:
	git config blame.ignoreRevsFile .git-blame-ignore-revs
	pre-commit install

test-backend:
	$(COMPOSE) run --rm --no-deps backend pytest .

test-frontend:
	$(COMPOSE) run --rm --no-deps frontend yarn test:ci
