# images=(python-prod-base aggregator api worker mocks nginx_reverse_proxy)
images=(python-prod-base api aggregator worker user_added_metrics mocks nginx_reverse_proxy)
IMG_NAMESPACE=ghcr.io/aignostic

for target in "${images[@]}"
do
	IMAGE_NAME=$IMG_NAMESPACE/$target
	echo "[x] Pushing $IMAGE_NAME for target $target"
	docker push $IMAGE_NAME
done