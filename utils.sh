#!/bin/bash

. config.sh

function debug() {
    echo -e "[\x1b[95mdebug\x1b[0m] $@"
}

function info() {
    echo -e "[\x1b[32minfo\x1b[0m] $@"
}

function error() {
    echo -e "[\x1b[31merror\x1b[0m] $@"
}

function error-check()
{
    if [[ $? != 0 ]]; then
        if [[ -n $1 ]]; then
            local MSG=$1
        else
            local MSG='Build failed.'
        fi
        error $MSG
        exit 1
    fi
}

function newer()
{
    if [[ -r "$1" ]]; then
        local SRC=$(stat -c %Y "$1")
    elif [[ -e "$1" ]]; then
        local SRC=$(sudo stat -c %Y "$1")
    else
        echo "error"
        return 0
    fi

    if [[ -r "$2" ]]; then
        local DST=$(stat -c %Y "$2")
    elif [[ -e "$2" ]]; then
        local DST=$(sudo stat -c %Y "$2")
    else
        echo "newer"
        return 1
    fi

    local DIFF=$(( DST - SRC ))
    if [[ $(( DST - SRC )) -lt 0 ]]; then
        echo "newer"
        return 1
    else
        echo "older"
        return 0
    fi
}


CPP_FLAGS='-P -undef -Wundef -std=c99 -nostdinc -Wtrigraphs -fdollars-in-identifiers -C'
CPP_FLAGS="$CPP_FLAGS -DDOMAIN=$DOMAIN -DWSS_PORT=$WSS_PORT"
if [[ $WS_UNSECURE == "true" ]]; then
    CPP_FLAGS="$CPP_FLAGS -DWSS_URL=\"ws://$DOMAIN:$WSS_PORT\""
else
    CPP_FLAGS="$CPP_FLAGS -DWSS_URL=\"wss://$DOMAIN:$WSS_PORT\""
fi

function update()
{
    local SRC=$1
    local DST=$2

    # If src is a directory
    if [[ -d "$SRC" ]]; then
        mkdir -p "$DST"
        for child in $(ls "$SRC"); do
            update "$SRC/$child" "$DST/$child"
        done
    # If src is a newer file
    elif [[ $(newer "$SRC" "$DST") == "newer" ]]; then
        echo "$SRC -> $DST"

        # If JS, run it through cpp
        if [[ "${SRC: -3}" == ".js" ]]; then
            # Configure JS
            cpp $CPP_FLAGS "$SRC" > "$SRC.conf"

            # Try to cp
            cp "$SRC.conf" "$DST" 2>/dev/null

            # If that fails, sudo it
            if [[ $? != 0 ]]; then
                sudo cp "$SRC.conf" "$DST"
            fi

            # Cleanup configured JS
            rm "$SRC.conf"
        else
            # Try to cp
            cp "$SRC" "$DST" 2>/dev/null

            # If that fails, sudo it
            if [[ $? != 0 ]]; then
                sudo cp "$SRC" "$DST"
            fi
        fi
    fi
}
