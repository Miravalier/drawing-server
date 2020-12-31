#!/bin/bash
function debug() {
    echo -e "[\x1b[95mdebug\x1b[0m] $@"
}

function info() {
    echo -e "[\x1b[32minfo\x1b[0m] $@"
}

function error() {
    echo -e "[\x1b[31merror\x1b[0m] $@"
}

# Update certs
sudo cp /etc/letsencrypt/live/miramontes.dev/fullchain.pem ./secrets
sudo cp /etc/letsencrypt/live/miramontes.dev/privkey.pem ./secrets
sudo chown -R $USER:$USER ./secrets

# Make sure the containers are not running.
if [[ $(docker-compose ps | wc -l) -gt 2 ]]; then
    info "Containers are running. Bringing them down."
    docker-compose down
    if [[ $? != 0 ]]; then
        error "Failed to bring containers down."
        exit 1
    fi
else
    info "Containers are not running."
fi

# Build the images.
info "Building images."
docker-compose build
if [[ $? != 0 ]]; then
    error "Failed to build images."
    exit 1
fi

# Bring the containers up.
info "Bringing containers up."
docker-compose up -d
if [[ $? != 0 ]]; then
    error "Failed to bring containers up."
    exit 1
fi

# Check if any immediately went into 'Exit' state and print their logs.
info "Displaying 'docker-compose ps'"
sleep 1
docker-compose ps
docker-compose logs --timestamps --tail=32

# Re deploy web app to miramontes.dev
./deploy.sh

# Return success
exit 0
