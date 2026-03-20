JASPR Docker Hub Quickstart

Goal
Run JASPR from a published container image with no local source checkout.

Prerequisites
- Docker Desktop or Docker Engine with Docker Compose v2
- Network access to Docker Hub

Fast Start
1. In a clean folder, copy docker-compose.deploy.yml from this repo.
2. Pull and start:
   docker compose -f docker-compose.deploy.yml pull
   docker compose -f docker-compose.deploy.yml up -d
3. Open the app in a browser:
   https://localhost

Stop
- docker compose -f docker-compose.deploy.yml down

Browser Access Model
- The container publishes host ports 80 and 443 by default.
- HTTP requests are redirected to HTTPS.
- Default URL is https://localhost.

Friendly Hostname Options
- Same machine alias:
  Add 127.0.0.1 localhost-jaspr to your hosts file, then browse to https://localhost-jaspr.
- Loopback domain option:
  Try https://localhost-jaspr.localhost.

Custom host on another machine
1. On the client machine, map a name to the server IP in DNS or hosts file.
2. Browse to https://your-custom-name.

Optional environment overrides
- JASPR_IMAGE (example: yourdockerhub/jaspr:single)
- JASPR_HTTP_PORT
- JASPR_HTTPS_PORT
- DEPLOYMENT_DNS

Windows hosts file location
- C:/Windows/System32/drivers/etc/hosts

Linux and macOS hosts file location
- /etc/hosts
