images=(python-prod-base api worker)
IMG_NAMESPACE=ghcr.io/aignostic

for target in "${images[@]}"
do
	IMAGE_NAME=$IMG_NAMESPACE/$target
	echo "Pushing $IMAGE_NAME for target $target"
	docker push $IMAGE_NAME
done