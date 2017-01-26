#! /usr/bin/env python
#-*- coding: utf-8 -*-

import sys
import re
from pyramid.paster import bootstrap, setup_logging
import StringIO
import locale
import logging
from argparse import ArgumentParser
from datetime import datetime, timedelta

import sqlahelper
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

import json
import urllib2
import contextlib
import transaction

import altair.multilock

from altair.pyramid_assets import get_resolver

from altair.app.ticketing.core.models import Organization, UserCredential
from altair.app.ticketing.users.models import Announcement, WordSubscription

from altair.app.ticketing.announce.utils import MacroEngine
from altair.muhelpers.mu import Mailer, Recipient

from altair.app.ticketing.api.impl import get_communication_api, CMSCommunicationApi

JOB_NAME = __name__

logger = logging.getLogger(__name__)

charset = locale.getpreferredencoding()
if charset == 'US-ASCII':
    charset = 'utf-8'

datetime_format = "%Y/%m/%d %H:%M"

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
    print >>output, (pad + repr(msg)).encode(charset)


def main():
    parser = ArgumentParser()
    parser.add_argument('--config', type=str, required=True)
    parser.add_argument('--result-from', type=str, required=True, help="ex. s3://bucket/path/from/download")
    parser.add_argument('--status-from', type=str, required=True, help="ex. s3://bucket/path/from/download")
    parser.add_argument('--quiet', action='store_true', default=False)
    parser.add_argument('--dry-run', action='store_true', default=False)
    parser.add_argument('--ahead', type=int, default=3*3600, help="process job in advance [sec]")

    opts = parser.parse_args()

    set_quiet(opts.quiet)

    setup_logging(opts.config)
    env = bootstrap(opts.config)
    request = env['request']
    session = sqlahelper.get_session()
    resolver = get_resolver(env['registry'])

    now = datetime.now()

    try:
        message("getting multilock as '%s'" % JOB_NAME)
        with altair.multilock.MultiStartLock(JOB_NAME):
            # get announcement without trans_id
            announces = session.query(Announcement) \
                .filter(Announcement.send_after < now) \
                .filter(Announcement.started_at != None) \
                .filter(Announcement.mu_trans_id == None) \
                .filter(Announcement.mu_result == None) \
                .filter(Announcement.completed_at == None) \
                .all()

            for a in announces:
                filename = '%s_%d.json' % (a.send_after.strftime("%Y%m%d_%H%M"), a.id)
                message("filename=%s" % filename)
                json_key = resolver.resolve('/'.join([opts.result_from, filename])).get_key()
                if json_key.exists():
                    obj = json.loads(json_key.get_contents_as_string())
                    # {
                    #  u'ErrorMessage': u'TemplatePcHtml\u5165\u529b\u30d1\u30e9\u30e1\u30fc\u30bf\u304c\u4e0d\u6b63\u3067\u3059',
                    #  u'ErrorCode': u'1001',
                    #  u'@env': u'pro',
                    #  u'MailName': None,
                    #  u'MailId': u'10330',
                    #  u'@action': u'send',
                    #  u'TransId': None,
                    #  u'@version': u'1.0'
                    # }
                    if obj['ErrorCode'] == 0:
                        message("transId = %s" % obj['TransId'])
                        if not opts.dry_run:
                            a.mu_trans_id = obj['TransId']
                            a.save()
                            transaction.commit()
                            message("set mu_trans_id")
                    else:
                        message("errorCode = %s" % obj['ErrorCode'])
                        if not opts.dry_run:
                            a.mu_result = "refused"
                            a.save()
                            transaction.commit()
                            message("set result: refused")

                    if not opts.dry_run:
                        # TODO: move?
                        # json_key.delete()
                        pass
                else:
                    message("not found in s3: %s" % filename)

            status_list = resolver.resolve(opts.status_from).listdir()
            for status in sorted([x for x in status_list if x.endswith(".json")], reverse=True):
                json_key = resolver.resolve('/'.join([opts.status_from, status])).get_key()
                obj = json.loads(json_key.get_contents_as_string())
                # u'Lambda: {
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
                # }

                if obj['Lambda']['ErrorMessage'] is not None or obj['Lambda']['ErrorCode'] != '0':
                    # should skip this file
                    message("skip file with error: %s" % status)
                    continue

                for trans in obj['Lambda']['TransStatus']['ID']:
                    # FIXME: 1つずつ探すのは避ける方がよさそう
                    a = session.query(Announcement) \
                        .filter(Announcement.mu_trans_id == trans['TransId']) \
                        .first()
                    if a is None:
                        continue

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

    except:
        set_quiet(False)
        raise

    message("done")

    return 0
