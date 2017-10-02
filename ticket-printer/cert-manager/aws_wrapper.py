#! /usr/bin/env python
#-*- coding: utf-8 -*-

import sys
import os
from argparse import ArgumentParser

from pyramid.paster import bootstrap


def main():
    parser = ArgumentParser()
    parser.add_argument('script', type=str, action='store')
    parser.add_argument('--config', type=str, required=True)
    opts = parser.parse_args()

    env = bootstrap(opts.config)

    os.environ['AWS_ACCESS_KEY_ID'] = env['registry'].settings.get('s3.access_key')
    os.environ['AWS_SECRET_ACCESS_KEY'] = env['registry'].settings.get('s3.secret_key')

    os.system(opts.script)

main()
