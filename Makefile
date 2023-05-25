COMPOSE := docker compose

.PHONY: distclean setup test-backend test-frontend

distclean:
	$(COMPOSE) down --volumes

setup:
	git config blame.ignoreRevsFile .git-blame-ignore-revs
	pre-commit install

test-backend:
	$(COMPOSE) run --rm --no-deps backend pytest .

test-frontend:
	$(COMPOSE) run --rm --no-deps frontend yarn test:ci
