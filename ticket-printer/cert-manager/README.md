# PRE REQUIREMENTS

- dig
- git
- openssl
- aws route53 (and permission)
- keytool (in java)

# SETUP

```sh
./setup.sh
./dehydrated/dehydrated --register --accept-terms
```

# HOW TO USE

```
./renew.sh
```

# LIMITATION

chain.pem containing 2+ certificates is not supported.
