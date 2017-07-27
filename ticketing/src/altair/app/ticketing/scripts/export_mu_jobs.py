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

from altair.app.ticketing.announce.utils import MacroEngine, html_filter

from altair.muhelpers import IMuMailerFactory
from altair.muhelpers.mu import Recipient
from altair.muhelpers.s3 import MuS3ConnectionFactory
from altair.pyramid_boto.s3.connection import IS3ConnectionFactory

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
    print >>output, (pad + (msg if isinstance(msg, basestring) else repr(msg))).encode(charset)


def upload(uri, data, resolver, dry_run):
    key = resolver.resolve(uri).get_key()
    if key:
        if dry_run:
            message("DRY-RUN: %s" % uri)
        else:
            headers = { "Content-Type": "application/zip"}
            key.set_contents_from_string(data, headers=headers)
            message("upload successfully: %s" % uri)
            key.make_public()
            message("update acl successfully.")
    else:
        set_quiet(False)
        raise Exception("wrong uri: " % uri)


def create_recipients(request, session, announcement):
    api = get_communication_api(request, CMSCommunicationApi)

    # 1. 特定イベントに紐づくWord情報をAPIで一括取得(mergeも展開)
    words = dict()
    req = api.create_connection("/api/word/?backend_event_id=%d" % announcement.event_id)
    try:
        with contextlib.closing(urllib2.urlopen(req)) as res:
            cms_info = json.loads(res.read())
            for w in cms_info['words']:
                words[w['id']] = w
                if w['merge']:
                    for mw in w['merge']:
                        words[mw] = w
    except Exception, e:
        logger.error("cms info error: %s" % (e.message))
        raise
    message("found words in cms event: %s" % ", ".join([str(w) for w in words.keys()]))

    # 2. 今回の配送ジョブで指定されているWord IDをsplitする
    announce_words = [ int(w) for w in announcement.words.split(",") ]
    message("found words in ticketing job: %s" % announce_words)

    # 3. 上記2つのデータを組み合わせて、今回の配送ジョブで扱うWord情報を準備する
    word_ids = reduce(lambda x, y: x+y, [ [wid]+words[wid]['merge'] for wid in announce_words if wid in words.keys() ])
    word_ids = list(set(word_ids))

    # TODO: ジョブに含まれているのにAPIが返さなかったWord IDがある場合は、警告したい

    if len(word_ids) == 0:
        logger.warn("no words found for event_id=%d, announcement_id=%d" % (announcement.event_id, announcement.id))
        return [ ]

    # 5. Word IDから、ユーザ毎の購読ワードリストを構築する
    subscriptions = session.query(UserCredential.auth_identifier, WordSubscription.word_id) \
        .filter(WordSubscription.word_id.in_(word_ids)) \
        .filter(WordSubscription.user_id == UserCredential.user_id) \
        .all()

    for (open_id, word_id) in subscriptions:
        message("user=%s word_id=%d" % (open_id, word_id))

    by_user = dict()
    for (open_id, word_id) in subscriptions:
        label = words[word_id]['label']
        if open_id not in by_user:
            by_user[open_id] = dict(words=[])
        if label not in by_user[open_id]['words']:
            by_user[open_id]['words'].append(label)
        # ここのソート順は気にしなくて良いか?

    for (open_id, attr) in by_user.items():
        message("user=%s words=%s" % (open_id, ", ".join(attr['words'])))

    return [Recipient(open_id, dict(keyword=", ".join(attr['words']))) for open_id, attr in by_user.items()]


def main():
    parser = ArgumentParser()
    parser.add_argument('--config', type=str, required=True)
    parser.add_argument('--organization', type=str, required=True)
    parser.add_argument('--target', type=str, required=True, help="ex. s3://bucket/path/to/upload")
    parser.add_argument('--quiet', action='store_true', default=False)
    parser.add_argument('--dry-run', action='store_true', default=False)
    parser.add_argument('--ahead', type=int, default=24*3600, help="process job in advance [sec]")

    opts = parser.parse_args()

    set_quiet(opts.quiet)

    setup_logging(opts.config)
    env = bootstrap(opts.config)
    request = env['request']
    session = sqlahelper.get_session()
    resolver = get_resolver(env['registry'])

    mu_factory = env['registry'].getUtility(IMuMailerFactory)
    mu = mu_factory()

    now = datetime.now()

    env['registry'].registerUtility(MuS3ConnectionFactory()(), IS3ConnectionFactory)

    try:
        try:
            organization = session.query(Organization) \
                .filter(
                    (Organization.id == opts.organization) \
                    | (Organization.short_name == opts.organization) \
                    | (Organization.name == opts.organization) \
                    | (Organization.code == opts.organization)) \
                .one()
        except NoResultFound:
            set_quiet(False)
            message('No such organization identifiable with %s' % opts.organization)
            return 1
        except MultipleResultsFound:
            set_quiet(False)
            message('Multiple organizations that match to %s' % opts.organization)
            return 1

        message("getting multilock as '%s'" % JOB_NAME, True)
        with altair.multilock.MultiStartLock(JOB_NAME):

            announces = session.query(Announcement) \
                .filter(Announcement.organization_id == organization.id) \
                .filter(Announcement.is_draft == 0) \
                .filter(Announcement.started_at == None) \
            .all()

            if len(announces) == 0:
                message("nothing to do", True)

            for a in announces:
                session.expunge(a)

            for _a in announces:
                if now + timedelta(seconds=opts.ahead) < _a.send_after:
                    message("announce(timer=%s, id=%d) -> skipped" % (_a.send_after, _a.id), True)
                    continue

                transaction.begin()

                a = session.query(Announcement).with_lockmode('update')\
                    .filter(Announcement.id == _a.id)\
                    .filter(Announcement.is_draft == 0) \
                    .filter(Announcement.started_at == None) \
                    .first()

                if a is None:
                    message("record was just updated and out of condition -> skipped")
                    transaction.rollback()
                    continue

                if now + timedelta(seconds=opts.ahead) < a.send_after:
                    message("announce(timer=%s, id=%d) -> skipped" % (a.send_after, a.id), True)
                    transaction.rollback()
                    continue

                message("announce(timer=%s, id=%d)" % (a.send_after, a.id))

                # prepare recipients
                recipients = create_recipients(request, session, a)
                message("found %d recipients" % len(recipients))

                # build message
                base_dict = dict()
                engine = MacroEngine()
                for f in engine.fields("".join([ a.subject, a.message ])):
                    label = engine.label(f)
                    base_dict[f] = a.parameters[label] if a.parameters.has_key(label) else ""
                body = engine.build(a.message, base_dict, cache_mode=True, filters=[html_filter])
                subject = engine.build(a.subject, base_dict, cache_mode=True)

                # make zip for postman (frontend of mu)
                mu.set_attributes(["keyword"])
                header = "X-TSA-Announce: %d" % a.id
                job_zip = mu.pack_as_zip(a.send_after, subject, body, recipients, header)

                # upload to s3
                dst = "%s/%s_%d.zip" % (opts.target.strip("/"), a.send_after.strftime("%Y%m%d_%H%M"), a.id)
                upload(dst, job_zip, resolver, opts.dry_run)

                if not opts.dry_run:
                    session.add(a)
                    a.started_at = datetime.now()
                    a.subscriber_count = len(recipients)
                    a.save()
                    transaction.commit()
                    message("set started")
                else:
                    transaction.rollback()

    except:
        set_quiet(False)
        raise

    message("done", True)

    return 0
