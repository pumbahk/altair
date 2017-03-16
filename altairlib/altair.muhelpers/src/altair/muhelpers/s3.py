from altair.pyramid_boto import DefaultS3ConnectionFactory


class MuS3ConnectionFactory(object):
    _instance = None

    def __init__(self, **kwargs):
        pass

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(MuS3ConnectionFactory, cls).__new__(cls)
            cls._instance.access_key = kwargs['access_key']
            cls._instance.secret_key = kwargs['secret_key']
        return cls._instance

    def __call__(self):
        return DefaultS3ConnectionFactory(self.access_key, self.secret_key)


def includeme(config):
    access_key = config.registry.settings.get('s3.mu.access_key')
    secret_key = config.registry.settings.get('s3.mu.secret_key')
    MuS3ConnectionFactory(access_key=access_key, secret_key=secret_key)
