#!/bin/bash

if [ "$1" = "minikube" ]; then
  eval $(minikube docker-env)
fi

kubectl apply -f secrets.yaml
kubectl apply -f configMap.yaml
kubectl apply -f frontend.yaml
kubectl apply -f training_manager.yaml
kubectl apply -f results_cache.yaml

