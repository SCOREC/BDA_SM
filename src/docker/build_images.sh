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
roottag="maxrpi/"
do_push="no"
while getopts "DmMp" options; do
  case "${options}" in
    D)
      roottag=""
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

${BUILDER} build -t ${roottag}training_manager${TMver} -f training_manager/Scripts/Dockerfile .
${BUILDER} build -t ${roottag}inference_manager${IMver} -f inference_manager/Scripts/Dockerfile .
${BUILDER} build -t ${roottag}sampler${Sver} -f sampler/Scripts/Dockerfile .
(cd frontend; ${BUILDER} build -t ${roottag}frontend${FRver} -f Scripts/Dockerfile .)
(cd results_cache; ${BUILDER} build -t ${roottag}results_cache${RCver} -f Scripts/Dockerfile .)
(cd fetcher; ${BUILDER} build -t ${roottag}fetcher${FETver} -f Scripts/Dockerfile .)

if [ ${do_push} == "no " ]; then
  echo "Not pushing to docker"
else
  echo "pushing to docker"
  docker push maxrpi/training_manager${TMver}
  docker push maxrpi/inference_manager${IMver}
  docker push maxrpi/sampler${Sver}
  docker push maxrpi/frontend${FRver}
  docker push maxrpi/results_cache${RCver}
  docker push maxrpi/fetcher${FETver}
fi

