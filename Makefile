COMPOSE_DEV := docker compose -f compose.yaml
COMPOSE_TEST := docker compose -f compose.test.yaml --env-file .env.test

.PHONY: confirm-email distclean integration-test-backend lint setup unit-test-backend unit-test-backend-dev unit-test-frontend unit-test-frontend-dev

confirm-email:
	$(COMPOSE_DEV) exec --no-TTY db psql --username=postgres postgres -c "UPDATE public.user SET confirmed_email=TRUE WHERE email='$(EMAIL)';"

distclean:
	$(COMPOSE_DEV) down --rmi local --volumes --remove-orphans
	$(COMPOSE_TEST) down --rmi local --volumes --remove-orphans

integration-test-backend:
	$(COMPOSE_TEST) up -d
	$(COMPOSE_TEST) exec --no-TTY backend-test pytest tests/integration; \
	$(COMPOSE_TEST) down --volumes

lint:
	pre-commit run --all-files --show-diff-on-failure

setup:
	git config blame.ignoreRevsFile .git-blame-ignore-revs
	pre-commit install

unit-test-backend:
	$(COMPOSE_TEST) run --no-TTY --rm --no-deps backend-test pytest tests/unit

unit-test-backend-dev:
	$(COMPOSE_DEV) run --no-TTY --rm --no-deps backend pytest tests/unit

unit-test-frontend:
	$(COMPOSE_TEST) run --no-TTY --rm --no-deps frontend-test yarn test

unit-test-frontend-dev:
	$(COMPOSE_DEV) run --no-TTY --rm --no-deps frontend yarn test
