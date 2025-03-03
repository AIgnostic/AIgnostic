#!/bin/bash

# python-prod-base is used to build the rest
# images=(python-prod-base aggregator api worker mocks nginx_reverse_proxy)
images=(python-prod-base api aggregator worker mocks nginx_reverse_proxy)
IMG_NAMESPACE=ghcr.io/aignostic

for target in "${images[@]}"
do
		IMAGE_NAME=$IMG_NAMESPACE/$target
		echo "Building $IMAGE_NAME for target $target"
		docker build --target $target -t $IMAGE_NAME -f ./dockerfiles/Dockerfile.python .
done

# Build nginx
# docker build --target nginx_reverse_proxy -t $IMG_NAMESPACE/nginx_reverse_proxy -f ./dockerfiles/Dockerfile.nginx.dockerfile .