# Build and Push the JASPR Single-Container Image

These steps build the portable, non-root JASPR image and publish it to
Docker Hub repository `cdcgov/jaspr` under two tags:

- `1.0`
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
    --pull=always --no-cache --format docker \
    -f build/docker/dockerfile-single \
    --label org.opencontainers.image.source="https://github.com/cdcent/jaspr" \
    --label org.opencontainers.image.url="https://hub.docker.com/r/cdcgov/jaspr" \
    --label org.opencontainers.image.documentation="https://github.com/cdcent/jaspr" \
    -t $IMAGE_PRIMARY \
    .
```

### Verify security before tagging or pushing

The image uses digest-pinned Chainguard Python build/runtime images
(Python 3.15.2, Expat 2.10.0), rather than Debian Bookworm. Pip, setuptools,
wheel, compilers, and the source tree are excluded from the final image.
It contains no shell or package manager.

Run the same security regression checks that run during the build and before
application startup:

```bash
podman run --rm --entrypoint python "$IMAGE_PRIMARY" /app/verify-image.py
```

Scan the actual image locally, not just the Dockerfile:

```bash
podman save --format docker-archive -o jaspr-image.tar "$IMAGE_PRIMARY"
podman run --rm -v "$PWD:/scan:ro" docker.io/aquasec/trivy:latest \
    image --input /scan/jaspr-image.tar --scanners vuln --exit-code 1
podman run --rm -v "$PWD:/scan:ro" docker.io/anchore/grype:latest \
    docker-archive:/scan/jaspr-image.tar --fail-on high
rm jaspr-image.tar
```

Scanner results can differ. Do not ignore new findings or assume a successful
build guarantees a clean scan. Grype's generic upstream-version matches can
still report locally backported fixes; review them against the table below.

| Advisory | Remediation / applicability in this image |
| --- | --- |
| CVE-2026-115506, CVE-2026-118370, CVE-2026-117610 | Both system Expat and Python's XML parser use fixed Expat 2.10.0. |
| CVE-2025-47273 | Runtime pip and setuptools, including the flagged pip BOM, are absent. Build tooling and the application build backend require patched setuptools. |
| CVE-2026-116566, GHSA-q27h-3599-9x7j | The pinned Python APKs are at the fixed version `3.15.2_git20261113-r0`; runtime checks confirm null bytes in host/port are rejected. Both identifiers describe the same issue. |
| CVE-2026-103995 | Official CPython HTTP framing fix and whitespace compatibility correction; unchecked-hash bytecode is removed so Python loads the patched source. |
| CVE-2026-84243 | Not applicable to the configured runtime: only C.utf8 is installed and a C messages locale is enforced at startup. The underlying glibc package is not claimed to be patched. |
| CVE-2026-119586 | Not applicable: this affects the SQLite CLI's `.recover` command; the image has the SQLite library but no CLI. |

The HTTP backport is in `build/docker/backport-python.sh` and is tied to the
CPython source revision of the pinned base images. The APK version does not
reflect this local patch, so scanners can still report CVE-2026-103995 without
a package-level fixed version. Update the builder/runtime digests together,
reassess the backport, and rerun regression checks and both scanners when
changing bases. `--pull=always` does not advance a pinned digest.
Do not install extra locales, enable a non-C message locale, or add the SQLite
CLI without reassessing the corresponding findings. Startup rejects those
changes.

Dependabot's manifest checks do not replace final-image scans. Re-scan published
images by digest as advisory databases change. Publishing is a separate step;
the checks above do not push anything to Docker Hub.

## 5. Tag

```bash
podman tag "$IMAGE_PRIMARY" "$IMAGE_LATEST"
```

## 6. Push

```bash
podman push "$IMAGE_PRIMARY"
podman push "$IMAGE_LATEST"
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
