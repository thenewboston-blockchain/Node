#!/usr/bin/env bash

set -e

RUN_MANAGE_PY='poetry run python -m node.manage'

# We need to collect static files to make WhiteNoise work (and we need to do it here)
# TODO(dmu) LOW: Collect static once, not on every run (we need to have named volume for it)
$RUN_MANAGE_PY collectstatic --no-input

$RUN_MANAGE_PY migrate --no-input
$RUN_MANAGE_PY assert_is_not_locked block

$RUN_MANAGE_PY sync_blockchain_with_network
$RUN_MANAGE_PY ensure_node_declared

# TODO(dmu) HIGH: Remove this work around once run-time syncing is implemented
#                 https://thenewboston.atlassian.net/browse/BC-247
sleep 1
$RUN_MANAGE_PY sync_blockchain_with_network

# TODO(dmu) MEDIUM: We might reconsider using `daphne` after figuring out if we have IO-bound or
#                   CPU-bound application
poetry run daphne -b 0.0.0.0 -p 8555 node.config.asgi:application
