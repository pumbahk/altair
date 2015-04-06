# -*- coding: utf-8 -*-
u"""fluentdが出力するログの解析器

fluentdが出力するログファイルのjsonのkeyを引数として渡す事でその値だけ
出力する事が出来ます。
"""


import sys
import json
import argparse


def main(argv):
    parser = argparse.ArgumentParser(usage=__doc__)
    parser.add_argument('-f', dest='input_file', type=argparse.FileType('r'), default=sys.stdin)
    parser.add_argument('keys', nargs='*', default=['message'])
    args = parser.parse_args(argv)

    for line in args.input_file:
        clock, domain, json_str = line.split('\t', 2)
        log = json.loads(json_str)
        log['clock'] = clock
        log['domain'] = domain
        try:
            print(' '.join([log[key] for key in args.keys]))
        except KeyError as err:
            print('KeyError: {} (you can use {})'.format(err, ', '.join(log.keys())))
