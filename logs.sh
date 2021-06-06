#!/bin/bash

. utils.sh

DOCKER_FLAGS='--env-file config_env'

docker-compose $DOCKER_FLAGS logs --timestamps -f

# Return success
exit 0
