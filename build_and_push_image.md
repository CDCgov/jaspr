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
export IMAGE_TAG_PRIMARY=single
export IMAGE_TAG_SECONDARY=latest

export IMAGE_PRIMARY=$IMAGE_REGISTRY/$IMAGE_USER/$IMAGE_NAME:$IMAGE_TAG_PRIMARY
export IMAGE_SECONDARY=$IMAGE_REGISTRY/$IMAGE_USER/$IMAGE_NAME:$IMAGE_TAG_SECONDARY
```

## 3. Log in to Docker Hub

Use your Docker Hub username. You will be prompted for password input.

```bash
docker login -u <username>
```

## 4. Build the image

```bash
docker build -f build/docker/dockerfile-single -t $IMAGE_PRIMARY .
```

## 5. Create the second tag

```bash
docker tag $IMAGE_PRIMARY $IMAGE_SECONDARY
```

## 6. Push both tags to cdcgov/jaspr

```bash
docker push $IMAGE_PRIMARY
docker push $IMAGE_SECONDARY
```

## 7. Optional: verify tags are pullable

```bash
docker pull $IMAGE_PRIMARY
docker pull $IMAGE_SECONDARY
```

## 8. Optional local run check

```bash
docker run -d --name jaspr_test -p 8080:80 -p 8443:443 $IMAGE_PRIMARY
```

Open:

```text
https://localhost:8443
```

Cleanup:

```bash
docker stop jaspr_test
docker rm jaspr_test
```
