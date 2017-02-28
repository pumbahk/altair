#! /usr/bin/env python
#-*- coding: utf-8 -*-

import sys

from beaker.cache import Cache
from pyramid.paster import bootstrap, setup_logging
import StringIO
import locale
import logging
from argparse import ArgumentParser
from datetime import datetime

import sqlahelper

import json
import transaction

import altair.multilock

from altair.pyramid_assets import get_resolver

from altair.app.ticketing.users.models import Announcement

from altair.muhelpers.s3 import MuS3ConnectionFactory
from altair.pyramid_boto.s3.connection import IS3ConnectionFactory


JOB_NAME = __name__

logger = logging.getLogger(__name__)

charset = locale.getpreferredencoding()
if charset == 'US-ASCII':
    charset = 'utf-8'

quiet = False

output = sys.stdout


def set_quiet(q):
    global quiet, output
    if q:
        output = StringIO.StringIO()
    else:
        if quiet:
            print >>sys.stdout, output.getvalue()
            output.close()
        output = sys.stdout
    quiet = q


def message(msg, auxiliary=False):
    logger.log(auxiliary and logging.DEBUG or logging.INFO, msg)
    pad = '  ' if auxiliary else ''
    print >>output, (pad + (msg if isinstance(msg, basestring) else repr(msg))).encode(charset)


def main():
    parser = ArgumentParser()
    parser.add_argument('--config', type=str, required=True)
    parser.add_argument('--result-from', type=str, required=True, help="ex. s3://bucket/path/from/download")
    parser.add_argument('--status-from', type=str, required=True, help="ex. s3://bucket/path/from/download")
    parser.add_argument('--quiet', action='store_true', default=False)
    parser.add_argument('--dry-run', action='store_true', default=False)

    opts = parser.parse_args()

    set_quiet(opts.quiet)

    setup_logging(opts.config)
    env = bootstrap(opts.config)
    request = env['request']
    session = sqlahelper.get_session()
    resolver = get_resolver(env['registry'])

    now = datetime.now()

    env['registry'].registerUtility(MuS3ConnectionFactory()(), IS3ConnectionFactory)

    try:
        message("getting multilock as '%s'" % JOB_NAME, True)
        with altair.multilock.MultiStartLock(JOB_NAME):
            # get announcement without trans_id
            announces = session.query(Announcement) \
                .filter(Announcement.started_at != None) \
                .filter(Announcement.mu_trans_id == None) \
                .filter(Announcement.mu_result == None) \
                .filter(Announcement.completed_at == None) \
                .all()

            for a in announces:
                session.expunge(a)

            for a in announces:
                filename = '%s_%d.json' % (a.send_after.strftime("%Y%m%d_%H%M"), a.id)

                # without cache mechanism
                json_key = resolver.resolve('/'.join([opts.result_from, filename])).get_key()
                if json_key.exists():
                    obj = json.loads(json_key.get_contents_as_string())
                    # { u'Lambda: {
                    #  u'ErrorMessage': u'TemplatePcHtml\u5165\u529b\u30d1\u30e9\u30e1\u30fc\u30bf\u304c\u4e0d\u6b63\u3067\u3059',
                    #  u'ErrorCode': u'1001',
                    #  u'@env': u'pro',
                    #  u'MailName': None,
                    #  u'MailId': u'10330',
                    #  u'@action': u'send',
                    #  u'TransId': None,
                    #  u'@version': u'1.0'
                    # } }
                    try:
                        if obj['Lambda']['ErrorCode'] == '0':
                            message("transId = %s" % obj['Lambda']['TransId'])
                            if not opts.dry_run:
                                session.add(a)
                                a.mu_trans_id = obj['Lambda']['TransId']
                                a.save()
                                transaction.commit()
                                message("set mu_trans_id", True)
                        else:
                            message("errorCode = %s" % obj['Lambda']['ErrorCode'])
                            if not opts.dry_run:
                                session.add(a)
                                a.mu_result = obj['Lambda']['ErrorCode']
                                a.save()
                                transaction.commit()
                                message("set error code from mu", True)
                                logger.warn('request is rejected by postman+mu by code: %s' % obj['Lambda']['ErrorCode'])
                    except Exception as e:
                        message("skip file with parse error in %s: %r" % (filename, e))
                        continue

                    if not opts.dry_run:
                        # TODO: move?
                        # json_key.delete()
                        pass
                else:
                    message("not found in s3: %s" % filename, True)

                    # startedしてから30分たっているのにtrans_idがないのは異常
                    age = (now - a.started_at).total_seconds()
                    if 30*60 < age:
                        logger.warn('mu request may not be processed: Announce.id=%d' % a.id)

            status_dir = resolver.resolve(opts.status_from)
            status_dir.retriever.entry_cache = Cache(__name__ + '.entry')   # disable redis cache
            status_list = status_dir.listdir()
            for status in sorted([x for x in status_list if x.endswith(".json")], reverse=True):
                json_key = resolver.resolve('/'.join([opts.status_from, status])).get_key()
                obj = json.loads(json_key.get_contents_as_string())
                # { u'Lambda: {
                #  u'ErrorMessage': None,
                #  u'ErrorCode': u'0',
                #  u'TransStatus': u'ID': [ {
                #    u'SendOkCount': u'3',
                #    u'@no': u'1',
                #    u'ProcResultFlg': u'1',
                #    u'AllListCount': u'3',
                #    u'ProcResultMessage': u'\u6b63\u5e38\u7d42\u4e86',
                #    u'TransId': u'156876',
                #    u'StatusMessage': u'\u9001\u4fe1\u7d42\u4e86',
                #    u'StatusCode': u'31'
                #  } ]
                # } }

                try:
                    if obj['Lambda']['ErrorMessage'] is not None or obj['Lambda']['ErrorCode'] != '0':
                        # should skip this file
                        message("skip file with error: %s" % status)
                        continue
                except Exception as e:
                    message("skip file with parse error in %s: %r" % (status, e))
                    continue

                message("parse status file: %s" % status, True)

                # 最新のstatusが3時間以上古いってのは、異常
                created_at = datetime.strptime(obj['Lambda']['created_at'], '%Y-%m-%d %H:%M:%S')
                age = (now - created_at).total_seconds()
                if 3*3600 < age:
                    logger.warn('latest status json from postman is too old: %s' % status)

                for trans in obj['Lambda']['TransStatus']['ID']:
                    # message("found trans_id=%s in status json" % trans['TransId'])

                    # FIXME: maybe slow
                    a = session.query(Announcement) \
                        .filter(Announcement.mu_trans_id == trans['TransId']) \
                        .filter(Announcement.mu_result == None) \
                        .filter(Announcement.completed_at == None) \
                        .first()
                    if a is None:
                        continue

                    message("found Announcement with trans_id=%s" % a.mu_trans_id, True)
                    if not opts.dry_run:
                        a.mu_status = trans['StatusCode']
                        if a.mu_result is None and trans['ProcResultFlg'] != '0':
                            message("set result: %s" % trans['ProcResultFlg'])
                            a.mu_result = trans['ProcResultFlg']
                            try:
                                a.mu_accepted_count = int(trans['AllListCount'])
                            except:
                                pass
                            try:
                                a.mu_sent_count = int(trans['SendOkCount'])
                            except:
                                pass
                            a.completed_at = datetime.now()
                        a.save()
                        transaction.commit()

                # 最新の1件を処理したら、終了する
                break

    except:
        set_quiet(False)
        raise

    message("done", True)

    return 0
