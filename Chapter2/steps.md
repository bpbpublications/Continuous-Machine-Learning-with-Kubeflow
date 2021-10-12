### Heart-Diseases Classification Use-Case : End to End Pipeline

### Pre-Requisite
- Follow the **setup-guides/steps-gcp.md** to setup kubeflow and required components. 

### Steps for End-To-End Pipeline


1. set working directory 
```bash
cd 04_Custom_Tensorflow_Sample 
WORKDIR=$(pwd)

```
Connect to GCP via Local
```bash
gcloud init
#Select the Email/Project associated with GCP

```

2. Build the container for Data Extraction

```bash
cd $WORKDIR/pipeline/dataextraction
PROJECT_ID=$(gcloud config get-value core/project)
IMAGE_NAME=breast_cancer/step1_loadingdata
IMAGE_VERSION=v1
IMAGE_NAME=gcr.io/$PROJECT_ID/$IMAGE_NAME
```

Building docker image. 
```
docker build -t $IMAGE_NAME:$IMAGE_VERSION .
```

Push training image to GCR
```
docker push $IMAGE_NAME:$IMAGE_VERSION
```


3. Build the container for Data preprocessing

```bash
cd $WORKDIR/pipeline/processing
PROJECT_ID=$(gcloud config get-value core/project)
IMAGE_NAME=breast_cancer/step2_dataprocessing
IMAGE_VERSION=v1
IMAGE_NAME=gcr.io/$PROJECT_ID/$IMAGE_NAME
```

Building docker image. 
```
docker build -t $IMAGE_NAME:$IMAGE_VERSION .

```
Push training image to GCR
```
docker push $IMAGE_NAME:$IMAGE_VERSION
```


4. Build the container for Training Model

```bash
cd $WORKDIR/pipeline/train
PROJECT_ID=$(gcloud config get-value core/project)
IMAGE_NAME=breast_cancer/step3_training_model
IMAGE_VERSION=v1
IMAGE_NAME=gcr.io/$PROJECT_ID/$IMAGE_NAME
```

Building docker image. 
```
docker build -t $IMAGE_NAME:$IMAGE_VERSION .
```
Push training image to GCR
```
docker push $IMAGE_NAME:$IMAGE_VERSION
```


5. Build the container for Evaluation Model

```bash
cd $WORKDIR/pipeline/evaluation 
PROJECT_ID=$(gcloud config get-value core/project)
IMAGE_NAME=breast_cancer/step4_evaluation_model
IMAGE_VERSION=v1
IMAGE_NAME=gcr.io/$PROJECT_ID/$IMAGE_NAME

```

Building docker image. 
```
docker build -t $IMAGE_NAME:$IMAGE_VERSION .
```
Push training image to GCR
```
docker push $IMAGE_NAME:$IMAGE_VERSION
```


### KFserving : Custom Image 

6. Build the container for Serving Model 


### Steps
Trained Model saved in the root of Docker file as the model folder is small

```bash
cd $WORKDIR/pipeline/serving 
PROJECT_ID=$(gcloud config get-value core/project)
IMAGE_NAME=breast_cancer/custom_serving_breastcancer
IMAGE_VERSION=v1
IMAGE_NAME=gcr.io/$PROJECT_ID/$IMAGE_NAME
```
```
Building docker image. 
```
docker build -t $IMAGE_NAME:$IMAGE_VERSION .
```
docker push $IMAGE_NAME:$IMAGE_VERSION
```


### Predict on a InferenceService using a KFServing Model Server

> Deploy using the KFServing client SDK

> Deploy using the command line


## Deploy using the command line
In the custom_breast_model.yaml file edit the container image and replace {username} with your Docker Hub username & give the same name as we provide in serving image python file

```bash
cd $WORKDIR/pipeline/serving 
# Connect to cluster
gcloud container clusters get-credentials <$ClusterName> --zone 
<$ZONE> --project <$PROJECTID>
# create the inference service
kubectl apply -f custom_breast_model.yaml
# check the inference service. Try it some interval to check if it has  been created. 
kubectl get inferenceservice -n kubeflow
```
Once the inference service is running. You can test using **curl**. 


```bash
#####
MODEL_NAME=kfserving-breast-model
HOST=$(kubectl get inferenceservice -n kubeflow $MODEL_NAME -o jsonpath='{.status.url}' | cut -d "/" -f 3)
INPUT_PATH=@./breast.json
CLUSTER_IP=$(kubectl -n istio-system get service kfserving-ingressgateway -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
curl -v -H "Host: ${HOST}" http://${CLUSTER_IP}/v1/models/${MODEL_NAME}:predict -d $INPUT_PATH
#####
```


#### Setup knative-monitoring
```bash
##RUN THE COMMAND IN GOOGLE SHELL
# Connect to cluster
gcloud container clusters get-credentials <$ClusterName> --zone 
<$ZONE> --project <$PROJECTID>
#create namespace
kubectl create namespace knative-monitoring
#setup monitoring components
kubectl apply --filename https://github.com/knative/serving/releases/download/v0.17.2/monitoring-metrics-prometheus.yaml
```

#### Launch grafana dashboard

```bash
# use port-forwarding
kubectl port-forward --namespace knative-monitoring $(kubectl get pod --namespace knative-monitoring --selector="app=grafana" --output jsonpath='{.items[0].metadata.name}') 8080:3000
```

open `grafana` dashboard by using `localhost:8080` on browser. Explore different components of the grafana dashboard. 
curl -v -H "Host: ${HOST}" http://${CLUSTER_IP}/v1/models/${MODEL_NAME}:predict -d $INPUT_PATH





To Debug you can use the following comamnds. 

```bash
# to describe the inference service
kubectl describe inferenceservice -n kubeflow  kfserving-breast-model

# to get the revision details. Replace the revision name from the output of the last command. 
kubectl get revision -n kubeflow <REVISION_NAME> -o yaml

# check the pods created
kubectl get pods -n kubeflow | grep kfserving-breast-model

# check the logs : check if the model files are loaded properly
kubectl logs -f <POD_NAME> -n kubeflow storage-initializer

# check the logs : check if the endpoint is running properly.
kubectl logs -f <POD_NAME>  -n kubeflow kfserving-container

# if you want to delete the inference service 
kubectl delete inferenceservice -n kubeflow kfserving-breast-model
or
kubectl delete -f custom_breast_model.yaml
```