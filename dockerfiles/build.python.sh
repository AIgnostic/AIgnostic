#!/bin/bash
images=(aggregator api worker)
IMG_NAMESPACE=aignostic

for target in "${images[@]}"
do
		IMAGE_NAME=$IMG_NAMESPACE/$target
		echo "Building $IMAGE_NAME for target $target"
		docker build --target $target -t $IMAGE_NAME -f ./dockerfiles/Dockerfile.python .
done