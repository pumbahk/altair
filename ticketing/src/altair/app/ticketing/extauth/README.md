h1. extauth


h2. テンプレート実装の手引

h3. アセットのs3へのアップロード

```
$ deploy/dev/bin/s3cmd sync --exclude='*.swp' --recursive -P --no-preserve ticketing/src/altair/app/ticketing/extauth/static/ s3://tstar-dev/extauth/static/
```

