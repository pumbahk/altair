#!/usr/bin/env python
# encoding: utf-8
import os
import sys
import logging
import transaction
import itertools
import logging
import argparse
import re
import csv
import locale
from datetime import date, datetime, timedelta
from dateutil.parser import parse as parsedate

from pyramid.paster import bootstrap, setup_logging

from sqlalchemy import func, or_, and_
from sqlalchemy.sql.expression import not_
from sqlalchemy.orm.exc import NoResultFound

import sqlahelper

logger = logging.getLogger(__name__)

formats = {
    'csv': csv.excel,
    'tsv': csv.excel_tab,
    }

class ApplicationException(Exception):
    pass

charset = locale.getpreferredencoding()

def message(msg, auxiliary=False):
    logger.log(auxiliary and logging.DEBUG or logging.INFO, msg)
    pad = '  ' if auxiliary else ''
    print >>sys.stderr, (pad + msg).encode(charset)

class RecordError(ApplicationException):
    @property
    def message(self):
        return self.args[0]
 
    @property
    def lineno(self):
        return self.args[1]
 
    def __str__(self):
        return '%s at line %d' % (self.message, self.lineno)

def do_import_user_data(request, session, membergroup_id, file_, encoding, format, dry_run=False):
    from altair.app.ticketing.users.models import UserProfile, User, MemberGroup, Membership, Member
    from altair.app.ticketing.core.models import Performance, PerformanceSetting, Organization

    membergroup = session.query(MemberGroup).filter_by(id=membergroup_id).one()
    membership = membergroup.membership

    now = datetime.now()
    f = open(file_)
    r = csv.reader(f, dialect=format)
    headers = [col.decode(encoding) for col in r.next()]
    l = 0

    def new_record_error(msg):
        raise RecordError(msg, l)

    def parse_int(s, msg):
        s = s.strip()
        if not s:
            return None
        try:
            return int(s)
        except (ValueError, TypeError):
            raise new_record_error('%s: %s' % (msg, s))

    def parse_long(s, msg):
        s = s.strip()
        if not s:
            return None
        try:
            return long(s)
        except (ValueError, TypeError):
            raise new_record_error('%s: %s' % (msg, s))

    def parse_date(s, msg, default_year=None):
        s = s.strip()
        if not s:
            return None
        g = re.match(u'(?:(?P<year>\d+)年)?(?P<month>\d+)月(?P<day>\d+)日', s)
        if g is not None:
            return date(
                year=parse_int(g.group('year'), msg) if g.group('year') else default_year,
                month=parse_int(g.group('month'), msg),
                day=parse_int(g.group('day'), msg)
                )
        try:
            return parsedate(s).date()
        except:
            raise new_record_error('%s: %s' % (msg, s))

    def parse_time(s, msg):
        s = s.strip()
        if not s:
            return None
        g = re.match(u'(?P<hour>\d+)時(?P<minute>\d+)分(?:(?P<second>\d+)秒)?', s)
        if g is not None:
            return time(
                hour=parse_int(g.group('hour'), msg),
                minute=parse_int(g.group('minute'), msg),
                second=parse_int(g.group('second'), msg)
                )
        try:
            return parsedate(s).time()
        except:
            raise new_record_error('%s: %s' % (msg, s))

    for l, row in enumerate(r, 2):
        cols = dict((headers[i], col.decode(encoding)) for i, col in enumerate(row))
        auth_identifier = cols[u'会員番号']
        auth_secret = cols[u'パスワード']
        last_name = cols[u'氏※全角10文字以内']
        first_name = cols[u'名※全角10文字以内']
        last_name_kana = cols[u'シ※全角10文字以内']
        first_name_kana = cols[u'メイ※全角10文字以内']
        email_1 = cols[u'E-mailアドレス']
        zip_ = cols[u'郵便番号']
        country = cols[u'国']
        prefecture = cols[u'都道府県']
        city = cols[u'市区町村']
        address_1 = cols[u'住所1']
        address_2 = cols[u'住所2']
        tel_1 = cols[u'電話番号1']

        message('importing User(auth_identifier=%s)' % (auth_identifier, ))

        if session.query(Member) \
            .filter(Member.membergroup_id == membergroup_id) \
            .filter(Member.auth_identifier == auth_identifier).count() > 0:
            message('User(auth_identifier=%s) already exists' % (auth_identifier, ))
            continue

        if not dry_run:
            user = User()
            user_profile = UserProfile(
                user=user,
                last_name=last_name,
                first_name=first_name,
                last_name_kana=last_name_kana,
                first_name_kana=first_name_kana,
                email_1=email_1,
                zip=zip_,
                country=country,
                prefecture=prefecture,
                city=city,
                address_1=address_1,
                address_2=address_2,
                tel_1=tel_1
                )
            member = Member(
                membergroup=membergroup,
                membership=membership,
                auth_identifier=auth_identifier,
                auth_secret=auth_secret
                )
            session.add(user_profile)
            session.add(user_credential)
            session.add(member)
            session.flush()

    if not dry_run:
        transaction.commit()

def main(argv=sys.argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('file', metavar='file', type=str)
    parser.add_argument('--config', metavar='config', type=str)
    parser.add_argument('--encoding', metavar='encoding', type=str)
    parser.add_argument('--format', metavar='format', type=str, default='csv')
    parser.add_argument('--membergroup-id', metavar='membergroup-id', type=long)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()

    setup_logging(args.config)
    env = bootstrap(args.config)
    request = env['request']

    session = sqlahelper.get_session()

    format = formats.get(args.format)
    if format is None:
        message("unknown format: %s" % format)
        return 255

    try:
        try:
            do_import_user_data(
                request,
                session,
                membergroup_id=args.membergroup_id,
                file_=args.file,
                encoding=args.encoding,
                format=formats[args.format],
                dry_run=args.dry_run
                )
        except ApplicationException as e:
            message(str(e))
            raise
    except:
        raise
    return 0

if __name__ == '__main__':
    sys.exit(main())

# vim: sts=4 sw=4 ts=4 et ai
