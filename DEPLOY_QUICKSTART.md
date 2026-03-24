JASPR Container Image Quickstart

Goal
Pull a published JASPR image and run it locally with either Docker or Podman.

Published image
```bash
export FULL_IMAGE=docker.io/cdcgov/jaspr:single
```

Pull and run with Docker
```bash
docker pull $FULL_IMAGE
docker run -d --name jaspr -p 8080:80 $FULL_IMAGE
```

Pull and run with Podman
```bash
podman pull $FULL_IMAGE
podman run -d --name jaspr -p 8080:80 $FULL_IMAGE
```

Browser access
- Open http://localhost:8080
- Using 8080 avoids privileged-port issues.

Optional easiest localhost mode (both HTTP and HTTPS)
```bash
docker run -d --name jaspr -p 80:80 -p 443:443 $FULL_IMAGE
podman run -d --name jaspr -p 80:80 -p 443:443 $FULL_IMAGE
```

Then open either:
- http://localhost
- https://localhost

If the browser shows "Your connection isn't private" for `https://localhost`, open `Advanced` and choose `Proceed to localhost`.

Friendly hostname on the same machine
1. Add this hosts-file entry:
   127.0.0.1 localhost-jaspr
2. Open one of:
   http://localhost-jaspr:8080
   https://localhost-jaspr

If the browser shows "Your connection isn't private" for the HTTPS option, open `Advanced` and choose `Proceed to localhost`.

Access from another machine
1. Map a DNS name or hosts-file entry to the server IP.
2. Browse to that name over HTTP.

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
