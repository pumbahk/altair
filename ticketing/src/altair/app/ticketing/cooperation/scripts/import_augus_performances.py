#-*- coding: utf-8 -*-
import os
import re
import csv
import argparse
from pit import Pit
from boto.s3.connection import S3Connection

import transaction
from pyramid.paster import bootstrap, setup_logging

from altair.app.ticketing.cooperation.augus import AugusPerformanceImpoter


class FileSearchError(Exception):
    pass

class AbnormalFormatError(Exception):
    pass

class AugusPeroformanceImportError(Exception):
    def __init__(self, *args, **kwds):
        pass
    
def augus_performance_s3_keys():
    #-------- modify ---------------------------------
    config = Pit.get('texample_s3_donwload',
                     {'require': {'access_key': '',
                                  'secret_key': '',
                                  'bucket_name': '',
                                  'path': '',
                                  }})
    access_key = config['access_key']
    secret_key = config['secret_key']
    bucket_name = config['bucket_name']
    path = config['path']
    #-------------------------------------------------
    regx = re.compile('^RT.*GME.*\.csv$', re.I)
    conn = S3Connection(access_key, secret_key)
    bucket = conn.get_bucket(bucket_name)
    for key in bucket.list(prefix=path):
        filename = os.path.basename(key.name)
        if regx.match(filename):
            yield key


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('config')
    args = parser.parse_args()
    env = bootstrap(args.config)
    request = env['request']
    importer = AugusPerformanceImpoter()
    tmp_file = 'tmp.csv'
    for key in augus_performance_s3_keys():
        key.get_contents_to_filename(tmp_file)
        with open(tmp_file, 'rb') as fp:
            reader = csv.reader(fp)
            try:
                importer.import_(reader)
            except Exception as err:
                transaction.abort()
                raise err
            else:
                transaction.commit()


if __name__ == '__main__':
    main()
