#!/bin/bash

if [ "$0" = "Cluster_start.sh" ]; then
   continue
else
   SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
   cd ${SCRIPT_DIR}/.
fi

KUBECTL=kubectl
mode="add"
secret_mode="file"
registry_mode="cli"
while getopts "mdrs:R:" options; do
  case "${options}" in
    R)
    registry="${OPTARG}/"
    mkdir -p ${registry}
    escregistry=$(echo ${registry} | sed "s/\//\\\\\//g")
    echo "Creating yaml files"
    for yaml in ./*.yaml
    do
      cat ${yaml} | sed "s/{{REGISTRY}}/${escregistry}/g" > ${registry}/${yaml}
    done
    ;;
    m)
      eval $(minikube docker-env)  
      ;;
    d)
      mode="delete"
      ;;
    r)
      registry_mode="file"
      ;;
    s)
      echo "Creating secrets from provided password"
      secret_mode="cli"
      server_secret=`echo -n ${OPTARG} | base64`
      s1=`cat /proc/sys/kernel/random/uuid | sed 's/[-]//g' | head -c 20 | base64`
      s2=`cat /proc/sys/kernel/random/uuid | sed 's/[-]//g' | head -c 20 | base64`
  esac
done

if [ "${mode}" = "delete" ]; then
  ${KUBECTL} delete -f ${registry}fetcher.yaml
  ${KUBECTL} delete -f ${registry}frontend.yaml
  ${KUBECTL} delete -f ${registry}inference_manager.yaml
  ${KUBECTL} delete -f ${registry}training_manager.yaml
  ${KUBECTL} delete -f ${registry}sampler.yaml
  ${KUBECTL} delete -f ${registry}results_cache.yaml
  ${KUBECTL} delete -f ${registry}configMap.yaml
  ${KUBECTL} delete -f ${registry}secrets.yaml
  ${KUBECTL} delete -f ${registry}registrykey.yaml
elif [ ${mode} = "add" ]; then
  if [ ${secret_mode} = "cli" ]; then
    ${KUBECTL} create secret generic bda-secrets \
      --from-literal=SERVER_SECRET=server_secret \
      --from-literal=SECRET_KEY="${s1}" \
      --from-literal=JWT_SECRET="${s2}" 
  else
    echo "Creating secrets from yaml file"
    ${KUBECTL} apply -f ${registry}secrets.yaml
  fi
  if [ ${registry_mode} = "cli" ]; then
    echo "Creating registrykey from yaml file"
    ${KUBECTL} create secret generic regcred  \
      --from-file=.dockerconfigjson=${HOME}/.docker/token.json \
      --type=docker.io/dockerconfigjson
  else
    echo "Creating registrykey from docker token file"
    ${KUBECTL} apply -f ${registry}registrykey.yaml
  fi 
  ${KUBECTL} apply -f ${registry}configMap.yaml
  ${KUBECTL} apply -f ${registry}frontend.yaml
  ${KUBECTL} apply -f ${registry}training_manager.yaml
  ${KUBECTL} apply -f ${registry}inference_manager.yaml
  ${KUBECTL} apply -f ${registry}results_cache.yaml
  ${KUBECTL} apply -f ${registry}sampler.yaml
  ${KUBECTL} apply -f ${registry}fetcher.yaml
fi
