#!/bin/bash

# python-prod-base is used to build the rest
images=(python-prod-base aggregator api worker)
IMG_NAMESPACE=ghcr.io/aignostic

for target in "${images[@]}"
do
		IMAGE_NAME=$IMG_NAMESPACE/$target
		echo "Building $IMAGE_NAME for target $target"
		docker build --target $target -t $IMAGE_NAME -f ./dockerfiles/Dockerfile.python .
done