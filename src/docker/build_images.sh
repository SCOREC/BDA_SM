#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd ${SCRIPT_DIR}/..

TMver=":v1.0"
IMver=":v1.0"
Sver=":v1.0"
FRver=":v1.0"
RCver=":v1.0"
FETver=":v1.0"

REVERSE='\033[7m'
BOLD='\033[1m'
NORMAL='\033[0m'
reverse() {
  echo -e "${REVERSE}"${*}"${NORMAL}\n"
}
bold() {
  echo -e "${BOLD}"${*}"${NORMAL}\n"
}

BUILDER=docker
roottag="maxrpi/"
do_push="no"
while getopts "DmMpA" options; do
  case "${options}" in
    D)
      roottag="maxrpi/"
      ;;
    A)
      roottag="maxrpicesmii.azurecr.io/bda/"
      ;;
    m)
      eval $(minikube docker-env)  
      roottag="mk/"
      ;;
    M)
      BUILDER='minikube image'
      ;;
    p)
      do_push="yes"
      ;;
  esac
done

reverse TRAINING_MANAGER
${BUILDER} build -t ${roottag}training_manager${TMver} -f training_manager/Scripts/Dockerfile .
reverse INFERENCE_MANAGER
${BUILDER} build -t ${roottag}inference_manager${IMver} -f inference_manager/Scripts/Dockerfile .
reverse SAMPLER
${BUILDER} build -t ${roottag}sampler${Sver} -f sampler/Scripts/Dockerfile .
reverse FRONTEND
(cd frontend; ${BUILDER} build -t ${roottag}frontend${FRver} -f Scripts/Dockerfile .)
reverse RESULTS_CACHE
(cd results_cache; ${BUILDER} build -t ${roottag}results_cache${RCver} -f Scripts/Dockerfile .)
reverse FETCHER
(cd fetcher; ${BUILDER} build -t ${roottag}fetcher${FETver} -f Scripts/Dockerfile .)

if [ ${do_push} == "no " ]; then
  echo "Not pushing to docker"
else
  echo "pushing to ${roottag}"
  reverse TRAINING_MANAGER
  docker push ${roottag}training_manager${TMver}
  reverse INFERENCE_MANAGER
  docker push ${roottag}inference_manager${IMver}
  reverse SAMPLER
  docker push ${roottag}sampler${Sver}
  reverse FRONTEND
  docker push ${roottag}frontend${FRver}
  reverse RESULTS_CACHE
  docker push ${roottag}results_cache${RCver}
  reverse FETCHER
  docker push ${roottag}fetcher${FETver}
fi

