### Build and Push Image

```bash
PROJECT_ID=$(gcloud config get-value core/project)
IMAGE_NAME=sso
IMAGE_NAME=gcr.io/$PROJECT_ID/$IMAGE_NAME
IMAGE_TAG=latest

# build image
docker build -t gcr.io/$PROJECT_ID/$IMAGE_NAME:$IMAGE_TAG .
# run locally to test
docker run -it --rm -p 8888:8888 -p 6006:6006 -v $(pwd):/home/jovyan gcr.io/$PROJECT_ID/$IMAGE_NAME:$IMAGE_TAG
# authorize docker
gcloud auth configure-docker --quiet
# push image
docker push gcr.io/$PROJECT_ID/$IMAGE_NAME:$IMAGE_TAG
```

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
- Add GPU 
- Click on **"Launch"**
- Upload the notebook `fashion-mnist-gpu.ipynb` and execute it. 
- Follow the instructions mentioned in the notebook