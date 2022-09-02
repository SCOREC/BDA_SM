#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd ${SCRIPT_DIR}/..

while getopts "m" options; do
  case "${options}" in
    m)
      eval $(minikube docker-env)  
      ;;
  esac
done

docker build -t ${roottag}training_manager -f training_manager/Scripts/Dockerfile .
docker build -t ${roottag}frontend -f frontend/Scripts/Dockerfile frontend/.
docker build -t ${roottag}results_cache -f results_cache/Scripts/Dockerfile results_cache/.
docker build -t ${roottag}fetcher -f fetcher/Scripts/Dockerfile fetcher/.