#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd ${SCRIPT_DIR}/..

TMver=":v1.0"
IMver=":v1.0"
Sver=":v1.0"
FRver=":v1.0"
RCver=":v1.0"
FETver=":v1.0"

BUILDER=docker
while getopts "DmM" options; do
  case "${options}" in
    D)
      roottag="maxrpi/"
      ;;
    m)
      eval $(minikube docker-env)  
      roottag="mk/"
      ;;
    M)
      BUILDER='minikube image'
  esac
done

${BUILDER} build -t ${roottag}training_manager${TMver} -f training_manager/Scripts/Dockerfile .
${BUILDER} build -t ${roottag}inference_manager${IMver} -f inference_manager/Scripts/Dockerfile .
${BUILDER} build -t ${roottag}sampler${Sver} -f sampler/Scripts/Dockerfile .
(cd frontend; ${BUILDER} build -t ${roottag}frontend${FRver} -f Scripts/Dockerfile .)
(cd results_cache; ${BUILDER} build -t ${roottag}results_cache${RCver} -f Scripts/Dockerfile .)
(cd fetcher; ${BUILDER} build -t ${roottag}fetcher${FETver} -f Scripts/Dockerfile .)
