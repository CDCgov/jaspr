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
export VERSION=1.0
export IMAGE_PRIMARY=docker.io/cdcgov/jaspr:$VERSION
export IMAGE_SECONDARY=docker.io/cdcgov/jaspr:latest

```

## 3. Log in to Docker Hub

Use your Docker Hub username. You will be prompted for password input.

```bash
podman login docker.io
```

## 4. Build the image

```bash
podman build -f build/docker/dockerfile-single --label org.opencontainers.image.source="https://github.com/cdcent/jaspr" --label org.opencontainers.image.url="https://hub.docker.com/r/cdcgov/jaspr" --label org.opencontainers.image.documentation="https://github.com/cdcent/jaspr" -t $IMAGE_PRIMARY .
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

For easiest local use with either protocol on plain `localhost`, publish both standard web ports:

```bash
podman run -d --name jaspr -p 80:80 -p 443:443 $IMAGE_PRIMARY
```

Open:

```text
http://localhost
https://localhost
```

If the browser shows "Your connection isn't private" for `https://localhost`, open `Advanced` and choose `Proceed to localhost`.

If your environment cannot bind privileged ports, use high ports instead:

```bash
podman run -d --name jaspr -p 8080:80 -p 8443:443 $IMAGE_PRIMARY
```

Then open:

```text
http://localhost:8080
https://localhost:8443
```

If the browser shows "Your connection isn't private" for `https://localhost:8443`, open `Advanced` and choose `Proceed to localhost`.

Cleanup:

```bash
podman stop jaspr
podman rm jaspr
```
