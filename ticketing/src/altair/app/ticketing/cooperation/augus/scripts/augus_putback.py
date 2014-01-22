#! /usr/bin/env python
#-*- coding: utf-8 -*-
import os
import argparse
import logging
from pyramid.paster import bootstrap
from altair.augus.protocols import (
    PutbackRequest,
    PutbackResponse,
    PutbackFinish,
    )
from altair.augus.parsers import AugusParser

def get_settings(conf=None): 
    if conf:
        raise NotImplementedError()
    else:
        from pit import Pit
        return Pit.get('augus_ftp',
                       {'require': {'staging': '',
                                    'pending': '',
                                    }})
def mkdir_p(path):
    if not os.path.isdir(path):
        os.makedirs(path)

def main():
    parser = get_argument_parser()
    args = parser.parse_args()
    bootstrap(args.conf)    
    settings = get_settings(args.conf)
    staging = settings['staging']
    pending = settings['pending']
    
    mkdir_p(staging)
    mkdir_p(pending)
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--conf', default=None)
    args = parser.parse_args()
    settings = get_settings(args.conf)
    staging = settings['staging']
    pending = settings['pending']
    
    mkdir_p(staging)
    mkdir_p(pending)
    
    for name in filter(PutbackRequest.match_name, os.listdir(staging)):
        path = os.path.join(staging, name)
        request = AugusParser.parse(path)
        
if __name__ == '__main__':
    main()
