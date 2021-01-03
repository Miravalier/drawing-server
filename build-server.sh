#!/bin/bash

. config.sh
. utils.sh
DOCKER_FLAGS='--env-file config.sh'

# Update certs
mkdir -p secrets
update $FULLCHAIN secrets/fullchain.pem
update $PRIVKEY secrets/privkey.pem
sudo chown -R $USER:$USER secrets

# Make sure the containers are not running.
if [[ $(docker-compose $DOCKER_FLAGS ps | wc -l) -gt 2 ]]; then
    info "Containers are running. Bringing them down."
    docker-compose $DOCKER_FLAGS down
    if [[ $? != 0 ]]; then
        error "Failed to bring containers down."
        exit 1
    fi
else
    info "Containers are not running."
fi

# Build the images.
info "Building images."
docker-compose $DOCKER_FLAGS build
if [[ $? != 0 ]]; then
    error "Failed to build images."
    exit 1
fi

# Bring the containers up.
info "Bringing containers up."
docker-compose $DOCKER_FLAGS up -d
if [[ $? != 0 ]]; then
    error "Failed to bring containers up."
    exit 1
fi

# Check if any immediately went into 'Exit' state and print their logs.
info "Displaying 'docker-compose ps'"
sleep 1
docker-compose $DOCKER_FLAGS ps
docker-compose $DOCKER_FLAGS logs --timestamps --tail=32

# Return success
exit 0
