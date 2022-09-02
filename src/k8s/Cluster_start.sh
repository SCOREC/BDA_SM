#!/bin/bash

if [ "$0" = "Cluster_start.sh" ]; then
   continue
else
   SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
   cd ${SCRIPT_DIR}/.
fi

mode="add"
secret_mode="file"
while getopts "mds:" options; do
  case "${options}" in
    m)
      eval $(minikube docker-env)  
      ;;
    d)
      mode="delete"
      ;;
    s)
      echo "Creating secrets from provided password"
      secret_mode="cli"
      server_secret=`echo -n ${options} | base64`
      s1=`cat /proc/sys/kernel/random/uuid | sed 's/[-]//g' | head -c 20 | base64`
      s2=`cat /proc/sys/kernel/random/uuid | sed 's/[-]//g' | head -c 20 | base64`
  esac
done

if [ "${mode}" = "delete" ]; then
  kubectl delete -f fetcher.yaml
  kubectl delete -f frontend.yaml
  kubectl delete -f training_manager.yaml
  kubectl delete -f results_cache.yaml
  kubectl delete -f configMap.yaml
  kubectl delete -f secrets.yaml
elif [ ${mode} = "add" ]; then
  if [ ${secret_mode} = "cli" ]; then
    kubectl create secret generic bda-secrets \
      --from-literal=SERVER_SECRET=server_secret \
      --from-literal=SECRET_KEY="${s1}" \
      --from-literal=JWT_SECRET="${s2}" 
  else
    echo "Creating secrets from yaml file"
    kubectl apply -f secrets.yaml
  fi 
  kubectl apply -f configMap.yaml
  kubectl apply -f frontend.yaml
  kubectl apply -f training_manager.yaml
  kubectl apply -f results_cache.yaml
  kubectl apply -f fetcher.yaml
fi