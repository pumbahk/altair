#-*- coding: utf-8 -*-
import os
import argparse

def mkdir_p(path):
    if not os.path.isdir(path):
        os.makedirs(path)

def get_argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('conf', default=None)
    return parser


def get_settings(conf=None):
    #if conf:
    #    raise NotImplementedError()
    #else:
        from pit import Pit
        return Pit.get('augus_ftp',
                       {'require': {'url': '',
                                    'username': '',
                                    'password': '',
                                    'staging': '',
                                    'pending': '',
                                    }})


