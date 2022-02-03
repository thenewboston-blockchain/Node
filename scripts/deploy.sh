#!/usr/bin/env bash

set -e

DOCKER_REGISTRY_HOST=ghcr.io

# TODO(dmu) MEDIUM: Figure out a way to pass environment variables from github actions to
#                   this script instead of using positional arguments
GITHUB_USERNAME="${GITHUB_USERNAME:-$1}"
GITHUB_PASSWORD="${GITHUB_PASSWORD:-$2}"
RUN_GENESIS="${RUN_GENESIS:-$3}"

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

wget https://raw.githubusercontent.com/thenewboston-developers/Node/master/docker-compose.yml -O docker-compose.yml

test -f .env || touch .env
grep -q -o MONGO_INITDB_ROOT_PASSWORD .env || echo "MONGO_INITDB_ROOT_PASSWORD=$(xxd -l 16 -p /dev/urandom)" >>.env
grep -q -o TNB_SECRET_KEY .env || echo "TNB_SECRET_KEY=$(xxd -c 48 -l 48 -p /dev/urandom)" >>.env

docker-compose pull

if ! grep -q -o TNB_NODE_SIGNING_KEY .env; then
  TEMPORARY_NODE_SIGNING_KEY=0000000000000000000000000000000000000000000000000000000000000000
  TNB_NODE_SIGNING_KEY=$(docker-compose --log-level CRITICAL run --rm -e TNB_NODE_SIGNING_KEY=$TEMPORARY_NODE_SIGNING_KEY node poetry run python -m node.manage generate_signing_key)
  echo "TNB_NODE_SIGNING_KEY=$TNB_NODE_SIGNING_KEY" >>.env
fi

# TODO CRITICAL: Implement clear_blockchain Django management command
#                https://thenewboston.atlassian.net/browse/BC-196
# TODO CRITICAL: Implement initialize_blockchain
#                https://thenewboston.atlassian.net/browse/BC-201
# TODO CRITICAL: Implement sync_blockchain
#                https://thenewboston.atlassian.net/browse/BC-202
# TODO CRITICAL: Implement ensure_node_declared
#                https://thenewboston.atlassian.net/browse/BC-197

docker-compose up -d --force-recreate
docker logout $DOCKER_REGISTRY_HOST

if [ "$RUN_GENESIS" == True ]; then
  echo 'Running genesis'
  docker-compose --log-level CRITICAL run --rm node poetry run python -m node.manage genesis -f https://raw.githubusercontent.com/thenewboston-developers/Account-Backups/master/latest_backup/latest.json
else
  echo 'Not running genesis'
fi

counter=0
# TODO CRITICAL: Implement ensure_node_declared
#                https://thenewboston.atlassian.net/browse/BC-197
until $(curl --output /dev/null --silent --head --fail http://127.0.0.1:8555/); do
  counter=$(($counter + 1))
  if [ ${counter} -ge 12 ]; then
    echo 'Unable to start node.'
    docker-compose down
    exit 1
  fi

  echo "Node has not started yet, waiting 5 seconds for retry (${counter})"
  sleep 5
done

echo 'Node is up and running'
