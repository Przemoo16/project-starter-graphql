COMPOSE_DEV := docker compose -f compose.yaml
COMPOSE_TEST := docker compose -f compose.test.yaml --env-file .env.test

.PHONY: distclean integration-test-backend lint setup unit-test-backend unit-test-frontend

distclean:
	$(COMPOSE_DEV) down --volumes --remove-orphans
	$(COMPOSE_TEST) down --volumes --remove-orphans

integration-test-backend:
	$(COMPOSE_TEST) up -d
	$(COMPOSE_TEST) exec --no-TTY backend-test pytest tests/integration; \
	$(COMPOSE_TEST) down

lint:
	pre-commit run --all-files --show-diff-on-failure

setup:
	git config blame.ignoreRevsFile .git-blame-ignore-revs
	pre-commit install

unit-test-backend:
	$(COMPOSE_TEST) run --no-TTY --rm --no-deps backend-test pytest tests/unit

unit-test-frontend:
	$(COMPOSE_TEST) run --no-TTY --rm --no-deps frontend-test yarn test:ci
