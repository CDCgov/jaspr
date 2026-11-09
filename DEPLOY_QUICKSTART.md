# JASPR Container Image Quickstart

The JASPR single-container image is designed to run unchanged under
**Docker**, **Podman** (rootful or rootless), and **Singularity / Apptainer**.

It is built to satisfy the constraints of restricted environments such as a
Cloudera Data Platform client node:

- runs as a non-root user (UID/GID `1000`)
- listens on a non-privileged port (`8080`)
- writes only to `/tmp` at runtime
- performs no dynamic install or bootstrap on launch
- exec()s `uwsgi` directly with a fixed config baked into the image

The current build uses Chainguard Python 3.15.2 with Expat 2.10.0 and
targeted upstream Python security backports. It has no shell, pip, setuptools,
or compiler. Security regression checks run before the entrypoint execs
the tini/uWSGI process. See [build and security verification](build_and_push_image.md)
before publishing or changing the pinned base images.

TLS, when needed, is expected to be terminated upstream (host nginx, ingress,
load balancer, etc.).  The image itself only speaks HTTP.

## Published image

```bash
export FULL_IMAGE=docker.io/cdcgov/jaspr:single
```

## Docker

```bash
docker pull $FULL_IMAGE
docker run -d --name jaspr \
    --read-only --tmpfs /tmp:rw,size=512m,mode=1777 \
    --user 1000:1000 \
    --cap-drop=ALL --security-opt=no-new-privileges \
    -p 8080:8080 \
    $FULL_IMAGE
```

Then open <http://localhost:8080>.

**Note:** The app only listens on port `8080` (unprivileged port). Do not use `-p 80:80` or `-p 443:443`; TLS must be terminated upstream.

## Podman (rootless or rootful)

```bash
podman pull $FULL_IMAGE
podman run -d --name jaspr \
    --read-only --tmpfs /tmp:rw,size=512m,mode=1777 \
    --user 1000:1000 \
    --cap-drop=ALL --security-opt=no-new-privileges \
    -p 8080:8080 \
    $FULL_IMAGE
```

Then open <http://localhost:8080>.

**Note:** The app only listens on port `8080` (unprivileged port). Do not use `-p 80:80` or `-p 443:443`; TLS must be terminated upstream.

```bash
podman-compose -f podman-compose-single.yml up -d
```

## Singularity / Apptainer

Singularity always runs as the **invoking** user (your host UID/GID), the
image filesystem is mounted **read-only**, and only a small set of paths
(`/tmp`, `/var/tmp`, `$HOME`, `/proc`, `/sys`, `/dev`) are writable.  The
JASPR image is built so this just works.

### One-time: convert the OCI image to a SIF

If you have access to the OCI image (Docker Hub, registry, or local podman),
build a SIF on a machine where Singularity is available:

```bash
# from a registry
singularity build jaspr.sif docker://cdcgov/jaspr:single

# from a local podman/docker image (export first)
podman save -o jaspr-oci.tar cdcgov/jaspr:single
singularity build jaspr.sif docker-archive://jaspr-oci.tar
```

### Run

```bash
singularity run \
    --containall \
    --writable-tmpfs \
    --pwd /app \
    jaspr.sif
```

Flag notes:

- `--containall` isolates the container from host bind mounts you don't
  need (recommended on shared CDP nodes).
- `--writable-tmpfs` provides a writable `/tmp` overlay since the rest of
  the image stays read-only.
- `--pwd /app` ensures the working directory is the app dir so relative
  resource lookups (none today, but safer) behave consistently.

If your site's Singularity install does not allow `--writable-tmpfs`,
bind-mount a host writable directory onto `/tmp` instead:

```bash
mkdir -p $HOME/jaspr-tmp
singularity run \
    --containall \
    --bind $HOME/jaspr-tmp:/tmp \
    --pwd /app \
    jaspr.sif
```

The container always listens on `0.0.0.0:8080` inside the namespace.  Under
Singularity that is the same as `127.0.0.1:8080` on the host, so you can
reach it directly without port publishing:

```bash
curl http://127.0.0.1:8080/ping
```

To bind to a different host port, run inside an SSH tunnel or use a
front-end reverse proxy on the host.

## Stop / clean up

```bash
docker stop jaspr && docker rm jaspr
podman stop jaspr && podman rm jaspr
# Singularity:  Ctrl-C in the foreground, or `singularity instance stop jaspr`
# if started with `singularity instance start`.
```

## Troubleshooting

- **`bind: permission denied` on port 80/443** — expected; this image only
  uses 8080.  Republish to a different host port if needed (`-p 9090:8080`).
- **`Read-only file system` writing under `/var/log` or `/etc`** — the
  image is read-only by design; the app should never write outside `/tmp`.
  If you see this, it is a bug; please report.
- **`I have no name!` shell prompt under Singularity** — cosmetic; the
  container runs as your host UID which has no entry in the container's
  `/etc/passwd`.  The app does not depend on the username.
- **Stuck on `Redis connection refused`** — should not happen anymore;
  set `REDIS_HOST=` (empty) or simply omit the variable to skip Redis
  entirely.  Filesystem sessions under `/tmp/flask_session` are used in
  that case.
