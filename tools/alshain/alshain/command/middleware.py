# -*- coding: utf-8 -*-
import os
import optparse

LOG = '/tmp/altair'
REDISLOG = os.path.join(LOG, 'redis.log')
RABBITMQLOG = os.path.join(LOG, 'rabbitmq.log')


def mkdir_p(path):
    try:
        os.makedirs(path)
    except:
        pass


def start():
    mkdir_p(LOG)
    os.system('mysql.server start')
    os.system('nohup redis-server > {0} 2>&1 &'.format(REDISLOG))
    os.system('sudo postfix start')
    os.system('nohup rabbitmq-server -detacched > {0} 2>&1 &'.format(RABBITMQLOG))


def stop():
    os.system('sudo postfix stop')
    os.system('mysql.server stop')
    os.system('rabbitmqctl stop')


def restart():
    stop()
    start()

CMD_FUNC = {'start': start,
            'stop': stop,
            'restart': restart,
            }


def main(argv):
    parser = optparse.OptionParser()
    opts, args = parser.parse_args(argv)

    for cmd in args:
        func = CMD_FUNC[cmd]
        func()
