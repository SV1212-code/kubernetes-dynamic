# Flask + MySQL on Minikube (Ubuntu)

```
app/   app.py, requirements.txt, Dockerfile
k8s/   mysql.yaml (PVC + MySQL + Service), flask.yaml (Flask + NodePort Service)
```

## 1. Start minikube

```bash
minikube start
kubectl get nodes
```

Make sure your shell uses your **host Docker**, not minikube's internal Docker
(harmless if you never ran `minikube docker-env`):

```bash
eval $(minikube docker-env -u)
```

## 2. Build the image with host Docker and push to Docker Hub

```bash
cd app
export DH_USER=your_dockerhub_username

docker build -t $DH_USER/flask-k8s-demo:1.0 .
docker login                      # enter Docker Hub username + password/token
docker push $DH_USER/flask-k8s-demo:1.0
cd ..
```

## 3. Point the deployment at your image

```bash
sed -i "s/YOUR_DOCKERHUB_USERNAME/$DH_USER/" k8s/flask.yaml
```

## 4. Deploy (Kubernetes pulls the image from Docker Hub)

```bash
kubectl apply -f k8s/mysql.yaml
kubectl get pods -w               # wait until mysql is Running (Ctrl+C)

kubectl apply -f k8s/flask.yaml
kubectl get pods                  # flask-app should be Running
kubectl get pvc                   # mysql-pvc should be Bound
```

## 5. Open the app

```bash
minikube service flask-app --url
```

Open the printed URL (or `http://$(minikube ip):30050`).
Type a name, pick a profession, click **Add**. Click **Complete** to list every record.

## 6. Test persistence

```bash
kubectl delete pod -l app=mysql   # the Deployment recreates the pod
kubectl get pods -w               # wait for it to be Running again
```

Click **Complete** again. The records are still there because they live on `mysql-pvc`.

## Updating the app

Change the code, then build and push a new tag and roll it out:

```bash
docker build -t $DH_USER/flask-k8s-demo:1.1 app
docker push $DH_USER/flask-k8s-demo:1.1
kubectl set image deployment/flask-app flask-app=$DH_USER/flask-k8s-demo:1.1
```

## Troubleshooting

```bash
kubectl logs deploy/flask-app
kubectl logs deploy/mysql
kubectl describe pod -l app=flask-app   # look for ImagePullBackOff (image name/tag wrong, or repo is private)
```

If you just clicked Add and got an error, MySQL may still be starting up. Wait about 30 seconds and try again.

## Clean up

```bash
kubectl delete -f k8s/flask.yaml -f k8s/mysql.yaml   # this also deletes the PVC and its data
```
