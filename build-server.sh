#!/bin/bash

. utils.sh

DOCKER_FLAGS='--env-file config.sh'

# Update certs
if [[ $WS_UNSECURE != "true" ]]; then
    mkdir -p secrets
    update $FULLCHAIN secrets/fullchain.pem
    update $PRIVKEY secrets/privkey.pem
    sudo chown -R $USER:$USER secrets
fi

# Make sure the containers are not running.
if [[ $(docker-compose $DOCKER_FLAGS ps | wc -l) -gt 2 ]]; then
    info "Containers are running. Bringing them down."
    docker-compose $DOCKER_FLAGS down
    error-check "Failed to bring containers down."
else
    info "Containers are not running."
fi

# Build the images.
info "Building images."
docker-compose $DOCKER_FLAGS build
error-check "Failed to build images."

# Bring the containers up.
info "Bringing containers up."
docker-compose $DOCKER_FLAGS up -d
error-check "Failed to bring containers up."

# Check if any immediately went into 'Exit' state and print their logs.
info "Displaying 'docker-compose ps'"
sleep 1
docker-compose $DOCKER_FLAGS ps
docker-compose $DOCKER_FLAGS logs --timestamps --tail=32

# Return success
exit 0
