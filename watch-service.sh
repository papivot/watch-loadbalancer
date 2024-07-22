#!/usr/bin/bash

TOKEN=$(grep 'token:' "$HOME"/.kube/config | awk '{print $2}')
APISERVER=$(grep 'server:' "$HOME"/.kube/config | awk '{print $2}')
HEADER="Authorization: Bearer $TOKEN"
NAMESPACE="demo1"
OBJECT="services"

response=$(curl -ks --write-out "%{http_code}" --header "$HEADER" "$APISERVER"/api/v1/namespaces/"$NAMESPACE"/"$OBJECT" --output temp_cluster.json)
if [[ "${response}" -ne 200 ]] ; then
    echo "Error: Could not fetch servicelist. Please validate!!"
    exit 1
fi

RES_VER=$(jq -r '.metadata.resourceVersion' temp_cluster.json)
if [ -z "${RES_VER}" ]
then
    echo "Error: Could not fetch valid RESOURCE VERSION. Please validate!!"
    exit 1
fi

CMD_OPT="resourceVersion=${RES_VER}&allowWatchBookmarks=true&watch=true"
curl -ks --no-buffer --write-out "%{http_code}" --header "$HEADER" "$APISERVER"/api/v1/namespaces/"$NAMESPACE"/"$OBJECT"?"$CMD_OPT" --output temp_svc.json
