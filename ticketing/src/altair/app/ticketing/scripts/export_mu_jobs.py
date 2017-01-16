#! /usr/bin/env python
#-*- coding: utf-8 -*-

import sys
import re
from pyramid.paster import bootstrap, setup_logging
import StringIO
import locale
import logging
from argparse import ArgumentParser
from datetime import datetime

import sqlahelper
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

import json
import urllib2
import contextlib

from altair.pyramid_assets import get_resolver

from altair.app.ticketing.core.models import Organization, UserCredential
from altair.app.ticketing.users.models import Announcement, WordSubscription

from altair.app.ticketing.announce.utils import MacroEngine
from altair.muhelpers.mu import Mailer, Recipient

from altair.app.ticketing.api.impl import get_communication_api, CMSCommunicationApi


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


def upload(uri, data, resolver, dry_run):
    key = resolver.resolve(uri).get_key()
    if key:
        if dry_run:
            message("DRY-RUN: %s" % uri)
            message("%s" % json.dumps(data))
        else:
            headers = { "Content-Type": "application/zip"}
            key.set_contents_from_string(data, headers=headers)
            message("upload successfully: %s" % uri)
            key.make_public()
            message("update acl successfully.")
    else:
        set_quiet(False)
        raise Exception("wrong uri: " % uri)


def main():
    parser = ArgumentParser()
    parser.add_argument('--config', type=str, required=True)
    parser.add_argument('--organization', type=str, required=True)
    parser.add_argument('--target', type=str, required=True, help="ex. s3://bucket/path/to/upload")
    parser.add_argument('--quiet', action='store_true', default=False)
    parser.add_argument('--dry-run', action='store_true', default=False)

    opts = parser.parse_args()

    set_quiet(opts.quiet)

    setup_logging(opts.config)
    env = bootstrap(opts.config)
    request = env['request']
    session = sqlahelper.get_session()
    resolver = get_resolver(env['registry'])

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

        # now = datetime.now()

        announces = session.query(Announcement) \
            .filter(Announcement.organization_id == organization.id) \
            .filter(Announcement.is_draft == 0) \
            .filter(Announcement.started_at == None) \
        .all()

        api = get_communication_api(request, CMSCommunicationApi)

        for a in announces:
            message("announce(timer=%s, id=%d)" % (a.send_after, a.id))

            # FIXME: skip when send_after is too large

            engine = MacroEngine()

            base_dict = dict()
            for f in engine.fields(a.message):
                label = engine.label(f)
                base_dict[f] = a.parameters[label]
            body = engine.build(a.message, base_dict, cache_mode=True)

            # from ticketing db
            word_ids = sorted(a.words.split(","))

            words = dict()
            req = api.create_connection("/api/word/?backend_event_id=%d" % a.event_id)
            try:
                with contextlib.closing(urllib2.urlopen(req)) as res:
                    cms_info = json.loads(res.read())
                    for w in cms_info['words']:
                        words[w['id']] = w['label']
            except Exception, e:
                logger.error("cms info error: %s" % (e.message))
                return dict()

            word_ids_from_cms = sorted(words.keys())

            # TODO: word_idsとword_ids_from_cmsが違う場合にwarn?

            subscriptions = session.query(UserCredential.auth_identifier, WordSubscription.word_id) \
                .filter(WordSubscription.word_id.in_(word_ids)) \
                .filter(WordSubscription.user_id == UserCredential.user_id) \
                .all()

            by_user = dict()
            for s in subscriptions:
                open_id = s[0]
                if open_id not in by_user:
                    by_user[open_id] = dict(words=[ ])
                word = words[s[1]]
                by_user[open_id]['words'].append(word)
                # ここのソート順は気にしなくて良いか?

            recipients = [ Recipient(open_id, dict(keyword=", ".join(attr['words']))) for open_id, attr in by_user.items() ]

            m = Mailer()
            m.set_attributes([ "name", "keyword" ])
            zip = m.pack_as_zip(a.send_after, body, recipients)

            dst = "%s/%s_%d.zip" % (opts.target.strip("/"), a.send_after.strftime("%Y%m%d_%H%M"), a.id)

            upload(dst, zip, resolver, opts.dry_run)

            # TODO: update db, set started_at

    except:
        set_quiet(False)
        raise

    message("done")

    return 0
