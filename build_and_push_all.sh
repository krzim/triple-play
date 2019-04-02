#!/usr/bin/env bash

# switch to the base directory of the project
scriptdir="$(dirname "$0")"
cd "$scriptdir"

LOCAL_REG="URI to docker swarm registry"
NODE_REG="localhost:5000/"

# build all of the docker images in the directory

for arg in "$@"
do
    if [ "$arg" = "worker" ]
        then
            docker build -f worker/Dockerfile -t "${LOCAL_REG}worker" -t "${NODE_REG}worker" .
            docker push "${LOCAL_REG}worker"

    elif [ "$arg" = "umpire" ]
    then
        docker build -f umpire/Dockerfile -t "${LOCAL_REG}umpire" -t "${NODE_REG}umpire" .
        docker push "${LOCAL_REG}umpire"

    elif [ "$arg" = "api_gateway" ]
    then
        docker build -f api_gateway/Dockerfile -t "${LOCAL_REG}api_gateway" -t "${NODE_REG}api_gateway" .
        docker push "${LOCAL_REG}api_gateway"

    elif [ "$arg" = "hello_world" ]
    then
        docker build -t "${LOCAL_REG}hello_world" -t "${NODE_REG}hello_world" ./apps/hello_world/v1.0/
        docker push "${LOCAL_REG}hello_world"

    elif [ "$arg" = "app_sdk" ]
    then
        docker build -f app_sdk/Dockerfile -t "walkoff_app_sdk" -t "${LOCAL_REG}walkoff_app_sdk" -t "${NODE_REG}walkoff_app_sdk" ./app_sdk/
        docker push "${LOCAL_REG}walkoff_app_sdk"

    elif [ "$arg" = "all" ]
    then
        docker build -f worker/Dockerfile -t "${LOCAL_REG}worker" -t "${NODE_REG}worker" .
        docker push "${LOCAL_REG}worker"

        docker build -f umpire/Dockerfile -t "${LOCAL_REG}umpire" -t "${NODE_REG}umpire" .
        docker push "${LOCAL_REG}umpire"

        docker build -f api_gateway/Dockerfile -t "${LOCAL_REG}api_gateway" -t "${NODE_REG}api_gateway" .
        docker push "${LOCAL_REG}api_gateway"

        docker build -t "${LOCAL_REG}hello_world" -t "${NODE_REG}hello_world" ./apps/hello_world/v1.0/
        docker push "${LOCAL_REG}hello_world"

        docker build -f app_sdk/Dockerfile -t "walkoff_app_sdk" -t "${LOCAL_REG}walkoff_app_sdk" -t "${NODE_REG}walkoff_app_sdk" ./app_sdk/
        docker push "${LOCAL_REG}walkoff_app_sdk"
    fi
done
