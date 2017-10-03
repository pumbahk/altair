# PRE REQUIREMENTS

- dig
- git
- openssl
- aws route53 (and permission)
- aws s3 (and permission)
- keytool (in java)

# SETUP

```sh
deploy/dev/bin/altairpy ticket-printer/cert-manager/aws_wrapper.py --config deploy/dev/conf/altair.ticketing.batch.ini ticket-printer/cert-manager/setup.sh
( cd ticket-printer/cert-manager ; ./dehydrated/dehydrated --register --accept-terms )
```

# HOW TO USE

```
deploy/dev/bin/altairpy ticket-printer/cert-manager/aws_wrapper.py --config deploy/dev/conf/altair.ticketing.batch.ini ticket-printer/cert-manager/renew.sh
```

for production define ALTAIR_S3_BUCKET environment.

# LIMITATION

chain.pem containing 2+ certificates is not supported.
