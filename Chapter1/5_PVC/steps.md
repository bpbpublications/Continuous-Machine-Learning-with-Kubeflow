
## 1.Create a Filestore instance with 1TB of storage capacity
```bash
FS=[NAME FOR THE FILESTORE YOU WILL CREATE]
gcloud beta filestore instances create ${FS} \
    --project=${PROJECT} \
    --zone=${ZONE} \
    --tier=STANDARD \
    --file-share=name="volumes",capacity=1TB \
    --network=name="default"
```

## 2.Retrieve the IP address of the Filestore instance
```bash
FSADDR=$(gcloud beta filestore instances describe ${FS} \
     --project=${PROJECT} \
     --zone=${ZONE} \
     --format="value(networks.ipAddresses[0])")
```
## 3.Connect to the cluster which you have created
```bash
export ZONE=us-east1-c
export CLUSTER_NAME= {Your-cluster name}
gcloud container clusters get-credentials <CLUSTER_NAME>--zone <ZONE> --project <PROJECT>
```


## 4. Grant yourself cluster-admin privileges
```bash
ACCOUNT=$(gcloud config get-value core/account)
kubectl create clusterrolebinding core-cluster-admin-binding \
    --user ${ACCOUNT} \
    --clusterrole cluster-admin
 ```   
## 5.Download Helm
```bash
wget https://storage.googleapis.com/kubernetes-helm/helm-v2.11.0-linux-amd64.tar.gz
tar xf helm-v2.11.0-linux-amd64.tar.gz
sudo ln -s $PWD/linux-amd64/helm /usr/local/bin/helm
```

## 6.Create a file named rbac-config.yaml containing the following:

apiVersion: v1
kind: ServiceAccount
metadata:
        name: tiller
        namespace: kube-system
---
apiVersion: rbac.authorization.k8s.io/v1beta1
kind: ClusterRoleBinding
metadata:
        name: tiller
roleRef:
        apiGroup: rbac.authorization.k8s.io
        kind: ClusterRole
        name: cluster-admin
subjects:
        - kind: ServiceAccount
        name: tiller
        namespace: kube-system

## 7. Create the tiller service account and cluster-admin role binding.
```bash
kubectl apply -f rbac-config.yaml
```
## 8. Initialize Helm.
```bash
helm init --service-account tiller
```
## 9.Copy the namespace you can find by either running below command which will give list of namespace. Or from UI  Copy from the drop down and paste in Notepad example here : aniruddha-choudhury
```bash
kubectl get namespace
```
## 10. Deploy the NFS-Client Provisioner
```bash
helm install stable/nfs-client-provisioner --name nfs-cp --set nfs.server=${FSADDR} --set nfs.path=/volumes
watch kubectl get po -l app=nfs-client-provisioner
```
## 11.Make a Persistent Volume Claim
```bash
kubectl create -f persistent-volume-claim.yaml
```
## 12. Copy the PVC name from above and paste it in Jupyter Notebook in Kubeflow Workspace Volume Name
```bash
## paste the namespace here to get the name
kubectl get pvc -n {namespace}
```