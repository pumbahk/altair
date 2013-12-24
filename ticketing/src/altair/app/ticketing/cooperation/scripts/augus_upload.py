#! /usr/bin/env python
#-*- coding: utf-8 -*-
import os
import argparse
import urlparse
from altair.augus.transporters import FTPTransporter
from altair.augus.parsers import AugusParser

def get_settings(conf=None):
    if conf:
        raise NotImplementedError()
    else:
        from pit import Pit
        return Pit.get('augus_ftp',
                       {'require': {'url': '',
                                    'username': '',
                                    'password': '',
                                    'local': '',
                                    }})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--conf', default=None)
    args = parser.parse_args()
    settings = get_settings(args.conf)
    local = settings['local']

    url = urlparse.urlparse(settings['url'])
    transporter = FTPTransporter(hostname=url.netloc,
                                 username=settings['username'],
                                 password=settings['password'],
                                 )

    transporter.chdir(url.path)
    for name in os.listdir(local):
        if AugusParser.is_protocol(name):
            path = os.path.join(local, name)
            print 'UPLOAD: {} -> {}'.format(path, name)
            transporter.put(path, name)

if __name__ == '__main__':
    main()
