#!/bin/bash

# python-prod-base is used to build the rest
# images=(python-prod-base aggregator api worker mocks nginx_reverse_proxy)
images=(python-prod-base api aggregator worker user_added_metrics mocks nginx_reverse_proxy)

if [ $# -eq 0 ]; then
  selected_images=("${images[@]}")
else
  selected_images=()
  for arg in "$@"; do
    if [[ " ${images[@]} " =~ " $arg " ]]; then
      selected_images+=("$arg")
    else
      echo "[!] Error: Invalid image name '$arg'"
      exit 1
    fi
  done
fi

IMG_NAMESPACE=ghcr.io/aignostic

# Print images to build
echo "[x] Building images: ${selected_images[@]}"
echo "[x] Namespace: $IMG_NAMESPACE"

for target in "${selected_images[@]}"
do
		IMAGE_NAME=$IMG_NAMESPACE/$target
		echo "[x] Building $IMAGE_NAME for target $target to tag $IMAGE_NAME"
		docker build --target $target -t $IMAGE_NAME -f ./dockerfiles/Dockerfile.python .
done

# Build nginx
# docker build --target nginx_reverse_proxy -t $IMG_NAMESPACE/nginx_reverse_proxy -f ./dockerfiles/Dockerfile.nginx.dockerfile .