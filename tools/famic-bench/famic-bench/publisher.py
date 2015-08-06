#! /usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import enum
import argparse
from kombu import Connection


@enum.unique
class ExitCode(enum.IntEnum):
    success = 0
    other_error = 254


def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser()
    parser.add_argument('reserve_numbers', nargs='?', type=argparse.FileType('r'), default=sys.stdin)
    args = parser.parse_args(argv)

    with Connection('amqp://guest:guest@localhost:5672//') as conn:
        receipt_queue = conn.SimpleQueue('receipt_queue')

        for reserve_number in args.reserve_numbers:
            reserve_number = reserve_number.strip()
            receipt_queue.put(reserve_number)
            print('publish: {}'.format(reserve_number))
        receipt_queue.close()
    return ExitCode.success.value


if __name__ == '__main__':
    sys.exit(main())
