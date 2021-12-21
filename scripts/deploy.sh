#!/usr/bin/env bash

set -e

DOCKER_REGISTRY_HOST=ghcr.io

# TODO(dmu) MEDIUM: Figure out a way to pass environment variables from github actions to
#                   this script instead of using positional arguments
GITHUB_USERNAME="${GITHUB_USERNAME:-$1}"
GITHUB_PASSWORD="${GITHUB_PASSWORD:-$2}"
GITHUB_BRANCH="${GITHUB_BRANCH:-$3}"
CLEAR_BLOCKCHAIN="${CLEAR_BLOCKCHAIN:-$4}"
CLEAR_BLOCKCHAIN="${CLEAR_BLOCKCHAIN:-False}"
INITIALIZE_FROM_ALPHA="${INITIALIZE_FROM_ALPHA:-$5}"
INITIALIZE_FROM_ALPHA="${INITIALIZE_FROM_ALPHA:-False}"

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

wget https://raw.githubusercontent.com/thenewboston-developers/Node/$GITHUB_BRANCH/docker-compose.yml -O docker-compose.yml

test -f .env || touch .env  # we need this file to exist, so grep does not fail
grep -q -o NODE_SECRET_KEY .env || echo "NODE_SECRET_KEY=$(dd bs=48 count=1 if=/dev/urandom | base64)" >> .env

docker-compose pull

#grep -q -o NODE_NODE_SIGNING_KEY .env || echo "NODE_NODE_SIGNING_KEY=$(docker-compose --log-level CRITICAL run --rm node poetry run python -m node.manage generate_signing_key)" >> .env
echo "NODE_NODE_SIGNING_KEY=48fd0c58f7b32f2eb3cdc6193db53fb1c478855347e3537935699ed158664e64">> .env

#if [ "$CLEAR_BLOCKCHAIN" == True ]; then
#  echo "Clearing blockchain..."
#  docker-compose run --rm node poetry run python -m thenewboston_node.manage clear_blockchain
#fi

echo "Running migrations..."
docker-compose run --rm node poetry run python -m node.manage migrate

#echo "Initializing blockchain (if it has not been initialized yet)..."
#if [ "$INITIALIZE_FROM_ALPHA" == True ]; then
#  docker-compose run --rm node bash -c 'poetry run python -m thenewboston_node.manage initialize_blockchain ${ARF_URL} ${ARF_PATH}'
#  # Syncing blockchain does not make sense if it was initialized from Alpha network, since
#  # we are creating the very first node of the Beta network and there is nothing to sync with
#else
#  docker-compose run --rm node bash -c 'poetry run python -m node.manage initialize_blockchain ${BLOCKCHAIN_STATE_PATH}*'
#
#  echo "Synchronizing blockchain..."
#  docker-compose run --rm node bash -c 'poetry run python -m node.manage sync_blockchain'
#  docker-compose run --rm node bash -c 'poetry run python -m node.manage ensure_node_declared'
#
#  # TODO(dmu) CRITICAL: Remove second sync once normal new block notification mechanism is implemented
#  docker-compose run --rm node bash -c 'poetry run python -m node.manage sync_blockchain'
#fi

docker-compose up -d --force-recreate
docker logout $DOCKER_REGISTRY_HOST

counter=0
until $(curl --output /dev/null --silent --head --fail http://127.0.0.1:8555/api/v1/nodes/self/); do
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
