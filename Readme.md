# JASPR: Curve Fitting and Report Generation for Antigenic Assay Analysis

JASPR is a curve-fitting and report-generation application for antigenic assay analysis used in viral surveillance workflows. Supported workflows include:

- **HINT** — High content Imaging-based Neutralization Test (Gubareva et al., 2019)
- **ICP** — Infected Cell Population (Gubareva et al., 2019)  
- **FRNT** — Focus Reduction Neutralization Test (Suthar et al., 2020)

## Quick Start

### Using Published Container Image

Run JASPR without checking out source code using the published Docker image.

#### Docker

```bash
docker pull docker.io/cdcgov/jaspr:1.0
docker run -d --name jaspr \
    --read-only --tmpfs /tmp:rw,size=512m,mode=1777 \
    --user 1000:1000 \
    --cap-drop=ALL --security-opt=no-new-privileges \
    -p 8080:8080 \
    docker.io/cdcgov/jaspr:1.0
```

#### Podman

```bash
podman pull docker.io/cdcgov/jaspr:1.0
podman run -d --name jaspr \
    --read-only --tmpfs /tmp:rw,size=512m,mode=1777 \
    --user 1000:1000 \
    --cap-drop=ALL --security-opt=no-new-privileges \
    -p 8080:8080 \
    docker.io/cdcgov/jaspr:1.0
```

Then open: **http://localhost:8080**

#### Stop the Container

```bash
docker stop jaspr && docker rm jaspr
podman stop jaspr && podman rm jaspr
```

### Security & Design Notes

The JASPR container is built for security and portability:

- **Non-root user** — Runs as UID/GID `1000` by design
- **Unprivileged port** — Listens on port `8080` only (no privileged ports)
- **Read-only filesystem** — Image is read-only; only `/tmp` is writable
- **No capabilities** — All Linux capabilities are dropped
- **TLS termination upstream** — Use a reverse proxy (nginx, ingress, etc.) for HTTPS

**Important:** Do not use `-p 80:80`, `-p 443:443`, or other privileged port mappings. The app only speaks HTTP on port `8080`.

### HTTPS with a Reverse Proxy

To expose JASPR over HTTPS with a domain name, use a reverse proxy on the host:

```nginx
upstream jaspr_backend {
    server 127.0.0.1:8080;
}

server {
    listen 443 ssl http2;
    server_name jaspr.example.com;

    ssl_certificate /etc/ssl/certs/jaspr.crt;
    ssl_certificate_key /etc/ssl/private/jaspr.key;

    location / {
        proxy_pass http://jaspr_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Documentation

- [DEPLOY_QUICKSTART.md](DEPLOY_QUICKSTART.md) — Container deployment, troubleshooting, and Singularity/Apptainer instructions

## Contributing

Anyone is encouraged to contribute to this repository by forking and submitting a pull request. By contributing to this project, you grant a world-wide, royalty-free, perpetual, irrevocable, non-exclusive, transferable license to all users under the terms of the [Apache Software License v2](http://www.apache.org/licenses/LICENSE-2.0.html) or later.

## Contact

For direct correspondence on the JASPR project:

- **Email:** ddidncirdflulimsdevelopers@cdc.gov
- **Division:** National Center for Immunization and Respiratory Diseases (NCIRD), Influenza Division (ID)
- **Agency:** Centers for Disease Control and Prevention (CDC)

## Notices

### Public Domain

This repository constitutes a work of the United States Government and is not subject to domestic copyright protection under 17 USC § 105. This repository is in the public domain within the United States, and copyright and related rights in the work worldwide are waived through the [CC0 1.0 Universal public domain dedication](https://creativecommons.org/publicdomain/zero/1.0/). All contributions to this repository will be released under the CC0 dedication. By submitting a pull request you are agreeing to comply with this waiver of copyright interest.

### License

The repository utilizes code licensed under the terms of the Apache Software License and therefore is licensed under ASL v2 or later. This source code in this repository is free: you can redistribute it and/or modify it under the terms of the Apache Software License version 2, or (at your option) any later version. This source code in this repository is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the Apache Software License for more details. You should have received a copy of the Apache Software License along with this program. If not, see: <http://www.apache.org/licenses/LICENSE-2.0.html>. The source code forked from other open source projects will inherit its license.

### Privacy

This repository contains only non-sensitive, publicly available data and information. All material and community participation is covered by the [Disclaimer](https://github.com/CDCgov/template/blob/main/DISCLAIMER.md). For more information about CDC's privacy policy, please visit <http://www.cdc.gov/other/privacy.html>.

### Records Management

This repository is not a source of government records, but is a copy to increase collaboration and collaborative potential. All government records will be published through the [CDC web site](http://www.cdc.gov).

### Additional Resources

Please refer to [CDC's Template Repository](https://github.com/CDCgov/template) for more information about:
- [Contributing to CDC repositories](https://github.com/CDCgov/template/blob/main/CONTRIBUTING.md)
- [Public domain notices and disclaimers](https://github.com/CDCgov/template/blob/main/DISCLAIMER.md)
- [Code of conduct](https://github.com/CDCgov/template/blob/main/code-of-conduct.md)

All comments, messages, pull requests, and other submissions received through CDC including this GitHub page may be subject to applicable federal law, including but not limited to the Federal Records Act, and may be archived. Learn more at [http://www.cdc.gov/other/privacy.html](http://www.cdc.gov/other/privacy.html).
