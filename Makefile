COMPOSE_DEV := docker compose -f compose.yaml
COMPOSE_TEST := docker compose -f compose.test.yaml --env-file .env.template --env-file .env.test
COMPOSE_E2E := docker compose -f compose.e2e.yaml --env-file .env.template --env-file .env.e2e

.PHONY: confirm-email distclean e2e-test integration-test-backend lint setup unit-test-backend unit-test-frontend

confirm-email:
	$(COMPOSE_DEV) exec --no-TTY db psql --username=postgres postgres -c "UPDATE public.user SET confirmed_email=TRUE WHERE email='$(EMAIL)';"

distclean:
	$(COMPOSE_DEV) down --rmi local --volumes --remove-orphans
	$(COMPOSE_TEST) down --rmi local --volumes --remove-orphans
	$(COMPOSE_E2E) down --rmi local --volumes --remove-orphans

e2e-test:
	$(COMPOSE_E2E) run --no-TTY --rm e2e; \
	exit_status=$$?; \
	$(COMPOSE_E2E) down; \
	exit $$exit_status

integration-test-backend:
	$(COMPOSE_TEST) run --no-TTY --rm backend-test pytest tests/integration; \
	exit_status=$$?; \
	$(COMPOSE_TEST) down; \
	exit $$exit_status

lint:
	pre-commit run --all-files --show-diff-on-failure

setup:
	git config blame.ignoreRevsFile .git-blame-ignore-revs
	pre-commit install

unit-test-backend:
	$(COMPOSE_TEST) run --no-TTY --rm --no-deps backend-test pytest tests/unit

unit-test-frontend:
	$(COMPOSE_TEST) run --no-TTY --rm --no-deps frontend-test yarn run test
