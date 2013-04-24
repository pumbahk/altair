from zope.interface import implementer
from boto.s3.connection import S3Connection
from ..interfaces import IS3ConnectionFactory

@implementer(IS3ConnectionFactory)
class DefaultS3ConnectionFactory(object):
    def __init__(self, access_key, secret_key, **options):
        self.access_key = access_key
        self.secret_key = secret_key

    def __call__(self):
        return S3Connection(self.access_key, self.secret_key) 
