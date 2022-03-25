#! /bin/bash
set -e

# setup basic auth? #
# if [ -z "${AUTH_USER}" -o -z "${AUTH_PASS}" ]
# then
#     echo "SETUP: No basic auth is being setup" 1>&2
# else
#     echo "SETUP: Using basic auth for nginx, user: ${AUTH_USER}" 1>&2
#     AUTH_CREDENTIAL="$(echo "${AUTH_PASS}" | openssl passwd -apr1 -noverify -stdin)"
#     echo "${AUTH_USER}:${AUTH_CREDENTIAL}" > /etc/nginx/.htpasswd
# fi

# link active certificate #
if [ -f "/credentials/ssl/${SSL_CERTIFICATE}.key" ]
then
    echo "SETUP: using certificate from /credentials/ssl" 1>&2
    ln -sf "/credentials/ssl/${SSL_CERTIFICATE}.key" /etc/ssl/certificate.key
    ln -sf "/credentials/ssl/${SSL_CERTIFICATE}.crt" /etc/ssl/certificate.crt
elif [ -f /etc/letsencrypt/live/$DEPLOYMENT_DNS/fullchain.pem ]
then
    echo "SETUP: using certificate from /etc/letsencrypt/live/$DEPLOYMENT_DNS" 1>&2
    ln -sf /etc/letsencrypt/live/$DEPLOYMENT_DNS/privkey.pem /etc/ssl/certificate.key
    ln -sf /etc/letsencrypt/live/$DEPLOYMENT_DNS/fullchain.pem /etc/ssl/certificate.crt
else
    echo "SETUP: using self-signed certificate in /etc/ssl" 1>&2
    ln -sf localhost.key /etc/ssl/certificate.key
    ln -sf localhost.crt /etc/ssl/certificate.crt
fi

# setup health check #
mkdir /opt/health ||:
rm /opt/health/index.html ||:
touch /opt/health/index.html
date >> /opt/health/index.html

# hotpatch NGINX to access /scicomp share files
# sed -E -i 's/user\s+nginx/user root/' /etc/nginx/nginx.conf
