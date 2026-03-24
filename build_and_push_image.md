# Build and Push JASPR Image

These steps publish the single-container image to Docker Hub repository:

- `cdcgov/jaspr`

with two tags:

- `single`
- `latest`

## 1. Go to the repository root

```bash
cd /path/to/jaspr
```

## 2. Set image values

```bash
export IMAGE_REGISTRY=docker.io
export IMAGE_USER=cdcgov
export IMAGE_NAME=jaspr
export IMAGE_TAG_PRIMARY=1.0
export IMAGE_TAG_SECONDARY=latest

export IMAGE_PRIMARY=$IMAGE_REGISTRY/$IMAGE_USER/$IMAGE_NAME:$IMAGE_TAG_PRIMARY
export IMAGE_SECONDARY=$IMAGE_REGISTRY/$IMAGE_USER/$IMAGE_NAME:$IMAGE_TAG_SECONDARY
```

## 3. Log in to Docker Hub

Use your Docker Hub username. You will be prompted for password input.

```bash
podman login docker.io
```

## 4. Build the image

```bash
podman build -f build/docker/dockerfile-single -t $IMAGE_PRIMARY .
```

## 5. Create the second tag

```bash
podman tag $IMAGE_PRIMARY $IMAGE_SECONDARY
```

## 6. Push both tags to cdcgov/jaspr

```bash
podman push $IMAGE_PRIMARY
podman push $IMAGE_SECONDARY
```

## 7. Optional: verify tags are pullable

```bash
podman pull $IMAGE_PRIMARY
podman pull $IMAGE_SECONDARY
```

## 8. Optional local run check

```bash
podman run -d --name jaspr_test -p 8080:80 $IMAGE_PRIMARY
```

Open:

```text
http://localhost:8080
```

Cleanup:

```bash
podman stop jaspr_test
podman rm jaspr_test
```
