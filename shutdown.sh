#!/bin/bash

. utils.sh
DOCKER_FLAGS='--env-file config_env'

# Take containers down
docker-compose $DOCKER_FLAGS down
error-check "Failed to bring containers down."

# Return success
exit 0
