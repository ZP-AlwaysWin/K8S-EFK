#!/bin/bash

/root/local/bin/kubectl delete configmap es-configmap
/root/local/bin/kubectl create configmap es-configmap --from-file=.