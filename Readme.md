## Notices

### Contact Info

For direct correspondence on the project, feel free to contact: ddidncirdflulimsdevelopers@cdc.gov, Centers for Disease Control and Prevention. 

### Public Domain Standard Notice

This repository constitutes a work of the United States Government and is not subject to domestic copyright protection under 17 USC § 105. This repository is in the public domain within the United States, and copyright and related rights in the work worldwide are waived through the [CC0 1.0 Universal public domain dedication](https://creativecommons.org/publicdomain/zero/1.0/).  All contributions to this repository will be released under the CC0 dedication.  By submitting a pull request you are agreeing to comply with this waiver of copyright interest.

### License Standard Notice

 The repository utilizes code licensed under the terms of the Apache Software License and therefore is licensed under ASL v2 or later. This source code in this repository is free: you can redistribute it and/or modify it under the terms of the Apache Software License version 2, or (at your option) any later version. This source code in this repository is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the Apache Software License for more details. You should have received a copy of the Apache Software License along with this program. If not, see: <http://www.apache.org/licenses/LICENSE-2.0.html>. The source code forked from other open source projects will inherit its license. The current configuration of DISC runs in Podman containers on RHEL8 OS VMs hosted by SciComp.
  
  ### Privacy Standard Notice

  This repository contains only non-sensitive, publicly available data and information. All material and community participation is covered by the [Disclaimer](https://github.com/CDCgov/template/blob/main/DISCLAIMER.md). For more information about CDC's privacy policy, please visit <http://www.cdc.gov/other/privacy.html>.

  ### Contributing Standard Notice

Anyone is encouraged to contribute to the repository by [forking](https://help.github.com/articles/fork-a-repo) and submitting a pull request. (If you are new to GitHub, you might start with a [basic tutorial](https://help.github.com/articles/set-up-git).) By contributing to this project, you grant a world-wide, royalty-free, perpetual, irrevocable, non-exclusive, transferable license to all users under the terms of the [Apache Software License v2](http://www.apache.org/licenses/LICENSE-2.0.html) or later.

  All comments, messages, pull requests, and other submissions received through CDC including this GitHub page may be subject to applicable federal law, including but not limited to the Federal Records Act, and may be archived. Learn more at [http://www.cdc.gov/other/privacy.html](http://www.cdc.gov/other/privacy.html).

  ### Records Management Standard Notice

This repository is not a source of government records, but is a copy to increase collaboration and collaborative potential. All government records will be published through the [CDC web site](http://www.cdc.gov).

### Additional Standard Notices

Please refer to [CDC's Template Repository](https://github.com/CDCgov/template) for more information about [contributing to this repository](https://github.com/CDCgov/template/blob/main/CONTRIBUTING.md), [public domain notices and disclaimers](https://github.com/CDCgov/template/blob/main/DISCLAIMER.md), and [code of conduct](https://github.com/CDCgov/template/blob/main/code-of-conduct.md).
 
### Contributing Standard Notice

For deployment to the production environment, follow the established strategy detailed here: (https://cdc-confluence.atlassian.net/wiki/spaces/FLULIMS/pages/8947258/JASPR)

## JASPR

### Container Image Quick Access

Use the published JASPR container image from Docker Hub without checking out source code.

JASPR is a curve-fitting and report-generation application for antigenic assay analysis used in viral surveillance workflows. Supported workflows include high content imaging-based neutralization test (HINT) (Gubareva et al., 2019), Infected Cell Population (ICP) (Gubareva et al., 2019), and Focus Reduction Neutralization Test (FRNT) (Suthar et al., 2020).

#### Quick Start

Run with Docker:

```bash
docker pull docker.io/cdcgov/jaspr:1.0
docker run -d --name jaspr \
    --read-only --tmpfs /tmp:rw,size=512m,mode=1777 \
    --user 1000:1000 \
    --cap-drop=ALL --security-opt=no-new-privileges \
    -p 8080:8080 \
    docker.io/cdcgov/jaspr:1.0
```

Run with Podman:

```bash
podman pull docker.io/cdcgov/jaspr:1.0
podman run -d --name jaspr \
    --read-only --tmpfs /tmp:rw,size=512m,mode=1777 \
    --user 1000:1000 \
    --cap-drop=ALL --security-opt=no-new-privileges \
    -p 8080:8080 \
    docker.io/cdcgov/jaspr:1.0
```

Then open:

```text
http://localhost:8080
```

#### Security & Design Notes

The JASPR container is built for security and portability:

- **Non-root user** — Runs as UID/GID `1000` by design
- **Unprivileged port** — Listens on port `8080` only (no privileged ports)
- **Read-only filesystem** — Image is read-only; only `/tmp` is writable
- **No capabilities** — All Linux capabilities are dropped
- **TLS termination upstream** — Use a reverse proxy (nginx, ingress, etc.) for HTTPS

**Important:** Do not use `-p 80:80`, `-p 443:443`, or other privileged port mappings. The app only speaks HTTP on port `8080`.

#### Stop the Container

```bash
docker stop jaspr && docker rm jaspr
podman stop jaspr && podman rm jaspr
```

#### Using a Reverse Proxy (nginx)

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

### Full Documentation

- [DEPLOY_QUICKSTART.md](DEPLOY_QUICKSTART.md) — Container deployment and troubleshooting


### Branch Strategy Notice

Core branches
- master -- This is deployed in the production environment
- jaspr_qa -- This is the primary branch in the QA environment

sudo su jaspr
cd ~ 
pwd
ls
cd jaspr

This is the primary branch on jaspr-prod: id-jaspr-prod-02.biotech.cdc.gov
Any bug fixes or feature add should be developed in a new branch. Create your new branch based on the `master` branch. 

Once your branch is ready for testing, merge it into the `QA` branch and deploy it to the QA environment. 

Create your new branch based on the master branch. 
Once your branch is ready for testing, merge it into the QA branch and deploy it to the jaspr-qa server: id-jaspr-qa-01.biotech.cdc.gov
 
Once testing on the QA branch is approved, merge the QA branch to master but make sure to not close/delete the QA branch.

Then, update the jaspr-prod server with master branch.






