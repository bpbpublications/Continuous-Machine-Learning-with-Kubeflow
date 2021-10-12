# create stream

```
PROJECT_ID=$(gcloud config get-value core/project)
IMAGE_NAME=lightgbm-serving
IMAGE_NAME=gcr.io/$PROJECT_ID/$IMAGE_NAME
IMAGE_TAG=v1

# build image

```bash
docker build  -t  $IMAGE_NAME:$IMAGE_TAG .
docker run -it --rm -p 8080:8080 $IMAGE_NAME:$IMAGE_TAG
docker push $IMAGE_NAME:$IMAGE_TAG
```

# KF Serving Inference

```bash
MODEL_NAME=kfserving-wandb-lightgbm-model
HOST=$(kubectl get inferenceservice -n kubeflow $MODEL_NAME -o jsonpath='{.status.url}' | cut -d "/" -f 3)
INPUT_PATH=@./input.json
CLUSTER_IP=$(kubectl -n istio-system get service kfserving-ingressgateway -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
curl -v -H "Host: ${HOST}" http://${CLUSTER_IP}/v1/models/${MODEL_NAME}:predict -d $INPUT_PATH
```

