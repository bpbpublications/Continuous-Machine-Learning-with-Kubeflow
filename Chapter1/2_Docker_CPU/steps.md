### Build and Push Image

```bash
PROJECT_ID=$(gcloud config get-value core/project)
IMAGE_NAME=custom-image-1
IMAGE_NAME=gcr.io/$PROJECT_ID/$IMAGE_NAME
IMAGE_TAG=latest
NAME=$IMAGE_NAME:$IMAGE_TAG 

# build image
docker build -t $IMAGE_NAME:$IMAGE_TAG .
# run locally to test
docker run -it --rm -p 8888:8888 -p 6006:6006 -v $(pwd):/home/jovyan $IMAGE_NAME:$IMAGE_TAG
# authorize docker
gcloud auth configure-docker --quiet
# push image
docker push $IMAGE_NAME:$IMAGE_TAG
```

### create Notebook

- Open Kubeflow central dashboard.
- Go to notebook servers
- Select namespace from the top drop-down
- Create notebook using create button
- Set the notebook name
- Use the custom image 
- set CPU, RAM, Workspace Volume, data volume
- Select config and select **"ADD GCP credentials"**
- Click on **"Launch"**


