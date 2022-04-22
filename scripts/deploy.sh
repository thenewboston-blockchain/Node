#!/usr/bin/env bash

set -e

DOCKER_REGISTRY_HOST=ghcr.io

# TODO(dmu) MEDIUM: Figure out a way to pass environment variables from github actions to
#                   this script instead of using positional arguments
GITHUB_USERNAME="${GITHUB_USERNAME:-$1}"
GITHUB_PASSWORD="${GITHUB_PASSWORD:-$2}"
RUN_GENESIS="${RUN_GENESIS:-$3}"

RUN_MANAGE_PY='poetry run python -m node.manage'
DOCKER_COMPOSE_RUN_MANAGE_PY="docker-compose run --rm node $RUN_MANAGE_PY"

docker logout $DOCKER_REGISTRY_HOST

# Support github actions deploy as well as manual deploy
if [[ -z "$GITHUB_USERNAME" || -z "$GITHUB_PASSWORD" ]]; then
  echo "Interactive docker registry login (username=github username; password=github personal access token (not github password)"
  docker login $DOCKER_REGISTRY_HOST
else
  echo "Automated docker registry login"
  # TODO(dmu) LOW: Implement a defensive technique to avoid printing password in case of `set -x`
  docker login --username "$GITHUB_USERNAME" --password "$GITHUB_PASSWORD" $DOCKER_REGISTRY_HOST
fi

echo 'Getting docker-compose.yml'
wget https://raw.githubusercontent.com/thenewboston-developers/Node/master/docker-compose.yml -O docker-compose.yml

echo 'Creating/updating .env file...'
test -f .env || touch .env
grep -q -o MONGO_INITDB_ROOT_PASSWORD .env || echo "MONGO_INITDB_ROOT_PASSWORD=$(xxd -l 16 -p /dev/urandom)" >> .env
grep -q -o TNB_SECRET_KEY .env || echo "TNB_SECRET_KEY=$(xxd -c 48 -l 48 -p /dev/urandom)" >> .env
grep -q -o TNB_NODE_SCHEDULE_CAPACITY .env || echo "TNB_NODE_SCHEDULE_CAPACITY=20" >> .env

docker-compose pull

grep -q -o TNB_NODE_SIGNING_KEY .env || echo "TNB_NODE_SIGNING_KEY=$(docker-compose --log-level CRITICAL run --rm -e TNB_NODE_SIGNING_KEY=dummy node $RUN_MANAGE_PY generate_signing_key)" >> .env

echo 'Waiting replica set initialization...'
docker-compose run --rm node poetry run python -m node.manage check_replica_set -w

if [ "$RUN_GENESIS" == True ]; then
  echo 'Running genesis...'
  # Test money
  # Private: a37e2836805975f334108b55523634c995bd2a4db610062f404510617e83126e
  # Public: 2e8c94aa1b8de49c41407fc3fce36785f56d6983ea6777dd9c7b25bfec95e4fc
  $DOCKER_COMPOSE_RUN_MANAGE_PY genesis -f -e 2e8c94aa1b8de49c41407fc3fce36785f56d6983ea6777dd9c7b25bfec95e4fc https://raw.githubusercontent.com/thenewboston-developers/Account-Backups/master/latest_backup/latest.json
else
  echo 'Syncing with the network...'
  $DOCKER_COMPOSE_RUN_MANAGE_PY sync_blockchain_with_network
fi

echo 'Ensuring the node is declared...'
$DOCKER_COMPOSE_RUN_MANAGE_PY ensure_node_declared

# TODO(dmu) HIGH: Remove this work around once run-time syncing is implemented
#                 https://thenewboston.atlassian.net/browse/BC-247
sleep 1
echo 'Syncing with the network...'
$DOCKER_COMPOSE_RUN_MANAGE_PY sync_blockchain_with_network

echo 'Starting the node...'
docker-compose up -d --force-recreate
docker logout $DOCKER_REGISTRY_HOST

echo 'Waiting the node to start...'
WAIT_PERIOD_SECONDS=10
counter=0
# TODO(dmu) MEDIUM: Check each address instead of just first
OWN_ADDRESS=$(docker-compose --log-level CRITICAL run --rm node $RUN_MANAGE_PY print_own_address blockchain --no-line-breaks --index 0)
CHECK_URL="${OWN_ADDRESS}api/nodes/self/"
until $(curl --output /dev/null --silent --fail $CHECK_URL); do
  counter=$(($counter + 1))
  if [ ${counter} -ge 12 ]; then
    echo "Unable to start node (checked at $CHECK_URL)"
    docker-compose down
    exit 1
  fi

  echo "Node has not started yet (checked at $CHECK_URL), waiting $WAIT_PERIOD_SECONDS seconds for retry (${counter})"
  sleep $WAIT_PERIOD_SECONDS
done

echo 'Node is up and running'
