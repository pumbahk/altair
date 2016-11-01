# -*- coding: utf-8 -*-
from boto.s3.connection import S3Connection
from boto.s3.key import Key


class S3ConnectionFactory(object):
    def __init__(self, request):
        self.access_key = request.registry.settings["s3.access_key"]
        self.secret_key = request.registry.settings["s3.secret_key"]

    def __call__(self):
        return S3Connection(self.access_key, self.secret_key, host='s3-ap-northeast-1.amazonaws.com')


def s3upload(connection, bucket_name, local_file_path, s3_directory_path, s3_file_name):
    s3_file_path = "{}{}".format(s3_directory_path, s3_file_name)
    bucket = connection.get_bucket(bucket_name)
    bucket_key = Key(bucket)
    bucket_key.key = s3_file_path
    bucket_key.set_contents_from_filename(local_file_path)
    bucket_key.set_acl('public-read')
