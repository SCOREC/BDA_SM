#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd ${SCRIPT_DIR}/..

BUILDER=docker
while getopts "mM" options; do
  case "${options}" in
    m)
      eval $(minikube docker-env)  
      roottag="mk/"
      ;;
    M)
      BUILDER='minikube image'
  esac
done

${BUILDER} build -t ${roottag}training_manager -f training_manager/Scripts/Dockerfile .
(cd frontend; ${BUILDER} build -t ${roottag}frontend -f Scripts/Dockerfile .)
(cd results_cache; ${BUILDER} build -t ${roottag}results_cache -f Scripts/Dockerfile .)
(cd fetcher; ${BUILDER} build -t ${roottag}fetcher -f Scripts/Dockerfile .)
