# Build and Push the JASPR Single-Container Image

These steps build the portable, non-root JASPR image and publish it to
Docker Hub repository `cdcgov/jaspr` under two tags:

- `single`
- `latest`

The image is the same one consumed by `DEPLOY_QUICKSTART.md` and is
designed to run unchanged under Docker, Podman, and Singularity.

## 1. Go to the repository root

```bash
cd /path/to/jaspr
```

## 2. Set image values

Set these environment variables in your shell session. They will be used in all subsequent steps:

```bash
export IMAGE_REGISTRY=docker.io
export IMAGE_USER=cdcgov
export IMAGE_NAME=jaspr
export VERSION=1.0
export IMAGE_PRIMARY=$IMAGE_REGISTRY/$IMAGE_USER/$IMAGE_NAME:$VERSION
export IMAGE_LATEST=$IMAGE_REGISTRY/$IMAGE_USER/$IMAGE_NAME:latest
```

Verify they are set correctly:

```bash
echo "PRIMARY: $IMAGE_PRIMARY"
echo "LATEST: $IMAGE_LATEST"
```

## 3. Log in to Docker Hub

```bash
podman login docker.io
```

**Important:** Keep the same shell session open for all remaining steps (4-6) so the environment variables from step 2 remain set.

## 4. Build the image

```bash
podman build \
    -f build/docker/dockerfile-single \
    --label org.opencontainers.image.source="https://github.com/cdcent/jaspr" \
    --label org.opencontainers.image.url="https://hub.docker.com/r/cdcgov/jaspr" \
    --label org.opencontainers.image.documentation="https://github.com/cdcent/jaspr" \
    -t $IMAGE_PRIMARY \
    .
```

## 5. Tag

```bash
podman tag docker.io/cdcgov/jaspr:1.0 docker.io/cdcgov/jaspr:latest
```

## 6. Push

```bash
podman push docker.io/cdcgov/jaspr:1.0
podman push docker.io/cdcgov/jaspr:latest
```

## 7. Optional local sanity-run

```bash
podman run -d --name jaspr \
    --read-only --tmpfs /tmp:rw,size=512m,mode=1777 \
    --user 1000:1000 \
    --cap-drop=ALL --security-opt=no-new-privileges \
    -p 8080:8080 \
    $IMAGE_PRIMARY

curl -fsS http://localhost:8080/ping
podman logs jaspr | head -50

podman stop jaspr
podman rm   jaspr
```

## 8. Optional Singularity sanity-run

On a host with Singularity / Apptainer:

```bash
singularity build jaspr.sif docker://$IMAGE_PRIMARY
singularity run --containall --writable-tmpfs --pwd /app jaspr.sif
# in another shell:
curl -fsS http://127.0.0.1:8080/ping
```

## Notes

- The image **always** runs as UID/GID `1000` and listens on
  `0.0.0.0:8080` internally.  Both are by design; do not override unless
  you also rebuild the image.
- TLS is **not** terminated inside the container.  Use a host-level
  reverse proxy (nginx, ingress controller, etc.) for HTTPS.
- The image filesystem is treated as read-only at runtime.  Only `/tmp`
  is written; mount additional volumes only if you want to persist
  uploads or session files.
