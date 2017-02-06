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

    words = dict()
    req = api.create_connection("/api/word/?backend_event_id=%d" % announcement.event_id)
    try:
        with contextlib.closing(urllib2.urlopen(req)) as res:
            cms_info = json.loads(res.read())
            for w in cms_info['words']:
                words[w['id']] = w['label']
    except Exception, e:
        logger.error("cms info error: %s" % (e.message))
        raise
    #message("found words in cms: %s" % ", ".join([str(w) for w in words.keys()]))

    #message("found words in job: %s" % ", ".join([str(w) for w in words.keys()]))

    announce_words = [ int(w) for w in announcement.words.split(",") ]

    # words is subset of cms word_ids
    # ignore id unless contained in cms word_ids
    word_ids = [ w for w in announce_words if w in words.keys() ]

    #message("search subscriptions for word_id: %s" % ", ".join([str(w) for w in word_ids]))

    if len(word_ids) == 0:
        logger.warn("no words found for event_id=%d, announcement_id=%d" % (announcement.event_id, announcement.id))
        return [ ]

    subscriptions = session.query(UserCredential.auth_identifier, WordSubscription.word_id) \
        .filter(WordSubscription.word_id.in_(word_ids)) \
        .filter(WordSubscription.user_id == UserCredential.user_id) \
        .all()

    by_user = dict()
    for s in subscriptions:
        open_id = s[0]
        if open_id not in by_user:
            by_user[open_id] = dict(words=[])
        word = words[s[1]]
        by_user[open_id]['words'].append(word)
        # ここのソート順は気にしなくて良いか?

    return [Recipient(open_id, dict(keyword=", ".join(attr['words']))) for open_id, attr in by_user.items()]


def main():
    parser = ArgumentParser()
    parser.add_argument('--config', type=str, required=True)
    parser.add_argument('--organization', type=str, required=True)
    parser.add_argument('--target', type=str, required=True, help="ex. s3://bucket/path/to/upload")
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

            for a in announces:
                if now + timedelta(seconds=opts.ahead) < a.send_after:
                    message("announce(timer=%s, id=%d) -> skipped" % (a.send_after, a.id), True)
                    continue

                message("announce(timer=%s, id=%d)" % (a.send_after, a.id))

                # prepare recipients
                recipients = create_recipients(request, session, a)
                message("found %d recipients" % len(recipients))

                # build message
                engine = MacroEngine()

                base_dict = dict()
                for f in engine.fields("".join([ a.subject, a.message ])):
                    label = engine.label(f)
                    base_dict[f] = a.parameters[label]
                body = engine.build(a.message, base_dict, cache_mode=True)
                subject = engine.build(a.subject, base_dict, cache_mode=True)

                mu.set_attributes(["keyword"])
                header = "X-TSA-Announce: %d" % a.id
                job_zip = mu.pack_as_zip(a.send_after, subject, body, recipients, header)

                dst = "%s/%s_%d.zip" % (opts.target.strip("/"), a.send_after.strftime("%Y%m%d_%H%M"), a.id)

                upload(dst, job_zip, resolver, opts.dry_run)

                if not opts.dry_run:
                    session.add(a)
                    a.started_at = datetime.now()
                    a.subscriber_count = len(recipients)
                    a.save()
                    transaction.commit()
                    message("set started")

    except:
        set_quiet(False)
        raise

    message("done", True)

    return 0
