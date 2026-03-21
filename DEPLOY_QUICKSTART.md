JASPR Container Image Quickstart

Goal
Build or pull a published JASPR image and run it with either Docker or Podman.

Why both work
- Docker Hub stores OCI-compatible container images.
- Podman and Docker can both build, push, pull, and run the same JASPR image.

Prerequisites
- Podman on RHEL 8.10 for build and push
- Network access to Docker Hub

Image variables
```bash
export IMAGE_REGISTRY=docker.io
export IMAGE_USER=yourdockerhubuser
export IMAGE_NAME=jaspr
export IMAGE_TAG=single
export FULL_IMAGE=$IMAGE_REGISTRY/$IMAGE_USER/$IMAGE_NAME:$IMAGE_TAG
```

Build and push from your RHEL 8.10 Podman environment
```bash
cd /path/to/jaspr
podman login docker.io
podman build -f build/docker/dockerfile-single -t $FULL_IMAGE .
podman push $FULL_IMAGE
```

Optional rolling tag
```bash
podman tag $FULL_IMAGE $IMAGE_REGISTRY/$IMAGE_USER/$IMAGE_NAME:latest
podman push $IMAGE_REGISTRY/$IMAGE_USER/$IMAGE_NAME:latest
```

Run with Docker
```bash
docker pull $FULL_IMAGE
docker run -d --name jaspr -p 8080:80 -p 8443:443 $FULL_IMAGE
```

Run with Podman
```bash
podman pull $FULL_IMAGE
podman run -d --name jaspr -p 8080:80 -p 8443:443 $FULL_IMAGE
```

Browser access
- Open https://localhost:8443
- JASPR redirects HTTP to HTTPS internally.
- Using 8080 and 8443 avoids privileged-port issues.

Optional 80 and 443 bindings
```bash
docker run -d --name jaspr -p 80:80 -p 443:443 $FULL_IMAGE
podman run -d --name jaspr -p 80:80 -p 443:443 $FULL_IMAGE
```

Then open https://localhost

Friendly hostname on the same machine
1. Add this hosts-file entry:
  127.0.0.1 localhost-jaspr
2. Open https://localhost-jaspr:8443

Access from another machine
1. Map a DNS name or hosts-file entry to the server IP.
2. Browse to that name over HTTPS.

Example client hosts entry
```text
192.168.1.50 localhost-jaspr
```

Stop and remove
```bash
docker stop jaspr && docker rm jaspr
podman stop jaspr && podman rm jaspr
```

Hosts file locations
- Windows: C:/Windows/System32/drivers/etc/hosts
- Linux and macOS: /etc/hosts
