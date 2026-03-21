# Build and Push JASPR Image

These steps are for building the JASPR single-container image from a RHEL 8.10 Podman environment and pushing it to Docker Hub.

## 1. Go to the repository root

```bash
cd /path/to/jaspr
```

## 2. Set your image values

Replace `yourdockerhubuser` if needed.

```bash
export IMAGE_REGISTRY=docker.io
export IMAGE_USER=yourdockerhubuser
export IMAGE_NAME=jaspr
export IMAGE_TAG=single
export FULL_IMAGE=$IMAGE_REGISTRY/$IMAGE_USER/$IMAGE_NAME:$IMAGE_TAG
```

## 3. Log in to Docker Hub from Podman

```bash
podman login docker.io
```

## 4. Build the single-container image

```bash
podman build -f build/docker/dockerfile-single -t $FULL_IMAGE .
```

## 5. Push the image to Docker Hub

```bash
podman push $FULL_IMAGE
```

## 6. Optional: push a rolling tag

```bash
podman tag $FULL_IMAGE $IMAGE_REGISTRY/$IMAGE_USER/$IMAGE_NAME:latest
podman push $IMAGE_REGISTRY/$IMAGE_USER/$IMAGE_NAME:latest
```

## 7. Optional local validation before moving to another machine

Run the image locally on non-privileged ports:

```bash
podman run -d --name jaspr_test -p 8080:80 -p 8443:443 $FULL_IMAGE
```

Open in a browser:

```text
https://localhost:8443
```

Stop and remove the test container:

```bash
podman stop jaspr_test
podman rm jaspr_test
```

## 8. On another computer, pull and run the image

With Podman:

```bash
export FULL_IMAGE=docker.io/yourdockerhubuser/jaspr:single
podman pull $FULL_IMAGE
podman run -d --name jaspr -p 8080:80 -p 8443:443 $FULL_IMAGE
```

With Docker:

```bash
export FULL_IMAGE=docker.io/yourdockerhubuser/jaspr:single
docker pull $FULL_IMAGE
docker run -d --name jaspr -p 8080:80 -p 8443:443 $FULL_IMAGE
```

Then open:

```text
https://localhost:8443
```

## 9. Optional localhost alias

Add this line to the hosts file on the machine where the browser is running:

```text
127.0.0.1 localhost-jaspr
```

Then browse to:

```text
https://localhost-jaspr:8443
```
