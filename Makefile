.PHONY: build
build: build-node build-reverse-proxy build-node-mongo;

.PHONY: build-node
build-node:
	docker build . --build-arg RESET_DOCKER_CACHE="$$(date)" --target=node -t node:current

.PHONY: build-reverse-proxy
build-reverse-proxy:
	docker build . --target=node-reverse-proxy -t node-reverse-proxy:current

.PHONY: build-node-mongo
build-node-mongo:
	docker build . --target=node-mongo -t node-mongo:current

.PHONY: up-dependencies-only
up-dependencies-only: build-node-mongo
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --force-recreate --build node-mongo mongo-express

.PHONY: up
up:
	docker-compose -f docker-compose.yml up --force-recreate

.PHONY: up-dev
up-dev: build
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --force-recreate

.PHONY: test
test:
	TNB_FOR_UNITTESTS_DISREGARD_OTHERWISE='{"test": 1}' poetry run pytest -v -rs -n auto --cov=node --cov-report=html --show-capture=no

.PHONY: test-stepwise
test-stepwise:
	poetry run pytest --reuse-db --sw -vv --show-capture=no

.PHONY: install
install:
	poetry install

.PHONY: migrate
migrate:
	 poetry run python -m node.manage migrate

.PHONY: install-pre-commit
install-pre-commit:
	poetry run pre-commit uninstall; poetry run pre-commit install

.PHONY: update
update: install migrate install-pre-commit ;

.PHONY: create-superuser
create-superuser:
	poetry run python -m node.manage createsuperuser

.PHONY: run-server
run-server:
	poetry run python -m node.manage runserver 127.0.0.1:8555

.PHONY: shell
shell:
	poetry run python -m node.manage shell

.PHONY: dbshell
dbshell:
	# TODO(dmu) LOW: Does it work with Djongo/MongoDB?
	poetry run python -m node.manage dbshell

.PHONY: lint
lint:
	poetry run pre-commit run --all-files

.PHONY: lint-and-test
lint-and-test: lint test ;

.PHONY: migrations
migrations:
	poetry run python -m node.manage makemigrations

.PHONY: genesis
genesis:
	poetry run python -m node.manage genesis -f https://raw.githubusercontent.com/thenewboston-developers/Account-Backups/master/latest_backup/latest.json

.PHONY: dot-env
dot-env:
	test -f .env || touch .env
	grep -q -o MONGO_INITDB_ROOT_PASSWORD .env || echo "MONGO_INITDB_ROOT_PASSWORD=$$(xxd -l 16 -p /dev/urandom)" >> .env
	grep -q -o TNB_SECRET_KEY .env || echo "TNB_SECRET_KEY=$$(xxd -c 48 -l 48 -p /dev/urandom)" >> .env
	grep -q -o TNB_NODE_SIGNING_KEY .env || echo "TNB_NODE_SIGNING_KEY=$$(poetry run python -m node.manage generate_signing_key)" >> .env
