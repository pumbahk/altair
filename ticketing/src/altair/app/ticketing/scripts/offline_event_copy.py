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
from datetime import date, time, datetime, timedelta
from dateutil.parser import parse as parsedate

from pyramid.paster import bootstrap, setup_logging

from sqlalchemy import sql
from sqlalchemy import orm
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

import sqlahelper

from altair.app.ticketing.core.clone import StringGenerators, CoreModelCloner

logger = logging.getLogger(__name__)

class ApplicationException(Exception):
    pass

charset = locale.getpreferredencoding()

def message(msg, auxiliary=False):
    logger.log(auxiliary and logging.DEBUG or logging.INFO, msg)
    pad = '  ' if auxiliary else ''
    print >>sys.stderr, (pad + msg).encode(charset)


class IDToken(object):
    def __init__(self, handler, serial):
        self.refcount = 1
        self.handler = handler
        self._serial = serial

    @property
    def serial(self):
        self._check_refcount()
        return self._serial

    def _check_refcount(self):
        if self.refcount == 0:
            raise ValueError('trying to use a disposed IDToken')

    def retain(self):
        self._check_refcount()
        self.refcount += 1

    def release(self):
        self._check_refcount()
        self.refcount -= 1
        if self.refcount == 0:
            self.handler._released(self, self._serial)


class Handler(object):
    def __init__(self, renderer):
        self.renderer = renderer
        self.serial = 1
        self.id_tokens = {}
        self.reuse_list = []

    def new_id_token(self):
        if len(self.reuse_list) > 0:
            serial = self.reuse_list.pop(0)
        else:
            serial = self.serial
            self.serial += 1
        id_token = IDToken(self, serial)
        self.id_tokens[serial] = id_token
        return id_token

    def _released(self, id_token, serial):
        del self.id_tokens[serial]
        self.reuse_list.append(serial)

    def _render_session_variable(self, v):
        return u'@id_%d' % v.serial

    def _filter_token(self, v):
        if isinstance(v, IDToken):
            assert self.id_tokens.get(v.serial) == v
            v = sql.text(self._render_session_variable(v))
        return v

    def _filter_tokens(self, columns):
        retval = {}
        for k, v in columns.items():
            v = self._filter_token(v)
            retval[k] = v 
        return retval

    def emit_insert(self, table, columns):
        columns = self._filter_tokens(columns)
        clause = sql.insert(table, columns)
        self.renderer(clause)

    def emit_insert_and_fetch_id(self, table, columns):
        self.emit_insert(table, columns)
        id_token = self.new_id_token() 
        self.renderer(sql.text(u'SET %s=LAST_INSERT_ID()' % self._render_session_variable(id_token)))
        return id_token

    def emit_update(self, table, column, id, columns):
        columns = self._filter_tokens(columns)
        clause = sql.update(table, whereclause=(table.c[column] == self._filter_token(id)), values=columns)
        self.renderer(clause)


class OurCoreModelCloner(CoreModelCloner):
    memory_profile = False

    def end_seat(self, seat):
        super(OurCoreModelCloner, self).end_seat(seat)
        session = orm.object_session(seat)
        if session is not None:
            session.expunge(seat.status_)
            for index in seat.indexes:
                session.expunge(index)
            session.expunge(seat)

    def begin_performance(self, performance):
        message(u'Start copying Performance(id=%ld, name=%s)' % (performance.id, performance.name))
        if self.memory_profile:
            import pympler.tracker, pympler.summary
            self.tracker = pympler.tracker.SummaryTracker()
        super(OurCoreModelCloner, self).begin_performance(performance)

    def end_performance(self, performance):
        super(OurCoreModelCloner, self).end_performance(performance)
        message(u'End copying Performance(id=%ld, name=%s)' % (performance.id, performance.name))
        if self.memory_profile:
            import pympler.tracker, pympler.summary
            for l in pympler.summary.format_(self.tracker.diff()):
                message(l)


def escape_param(dialect, value):
    if value is None:
        return u"NULL"
    elif isinstance(value, basestring):
        return u"'%s'" % value.replace("'", "''").replace('\\', '\\\\')
    elif isinstance(value, date):
        return u"'%s'" % value
    elif isinstance(value, time):
        return u"'%s'" % value
    else:
        return unicode(value) # XXX

def convert_placeholders(compiled_expr):
    stmt_str = str(compiled_expr)
    paramstyle = compiled_expr.dialect.paramstyle
    if paramstyle == 'named':
        if len(compiled_expr.params) > 0:
            named_param_re = ur'\b(%s)\b' % '|'.join(compiled_expr.params)
        else:
            named_param_re = None

    retval = []
    counter = itertools.count(0)
    for token in re.finditer(ur"""([^`'"]+)|(`(?:[^`]|``)*`)|('(?:[^']|\\'|'')*')|("(?:[^"]|\\"|"")*")""", stmt_str):
        unquoted = token.group(1)
        if unquoted is not None:
            if paramstyle == 'pyformat':
                unquoted = re.sub(ur'%\(([^)]+)\)s', lambda g: u'{%s}' % g.group(1), unquoted)
            elif paramstyle == 'qmark':
                unquoted = re.sub(ur'\?', lambda g: u'{%d}' % counter.next(), unquoted)
            elif paramstyle == 'format':
                unquoted = re.sub(ur'%s', lambda g: u'{%d}' % counter.next(), unquoted)
            elif paramstyle == 'numeric':
                unquoted = re.sub(ur':(\d+)', lambda g: u'{%d}' % (int(g.group(1)) - 1), unquoted)
            elif paramstyle == 'named':
                if named_param_re is not None:
                    unquoted = re.sub(named_param_re, lambda g: u'{%s}' % g.group(1), unquoted)
            retval.append(unquoted)
        else:
            retval.append(token.group(0))

    return ''.join(retval)

def render_sql(expr):
    compiled_expr = expr.compile()
    params = compiled_expr.params
    if compiled_expr.dialect.positional:
        positional = [
            escape_param(compiled_expr.dialect, params[k])
            for k in compiled_expr.positiontup
            ]
        named = {}
    else:
        positional = ()
        named = dict(
            (k, escape_param(compiled_expr.dialect, v))
            for k, v in params.items()
            )

    return convert_placeholders(compiled_expr).format(*positional, **named)


def do_event_copy(request, session, event):
    def renderer(clause):
        print(('%s;' % render_sql(clause)).encode(charset))

    handler = Handler(renderer)
    string_gen = StringGenerators()
    c = OurCoreModelCloner(handler, string_gen, event.organization)
    event.accept_core_model_traverser(c)

 
def main(argv=sys.argv):
    from altair.app.ticketing.core.models import Organization, Event
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', metavar='config', type=str)
    parser.add_argument('--organization', metavar='organization', type=str)
    parser.add_argument('event', metavar='event', nargs='+', type=str)
    args = parser.parse_args()

    setup_logging(args.config)
    env = bootstrap(args.config)
    request = env['request']

    session = sqlahelper.get_session()

    try:
        organization = None
        try:
            organization = session.query(Organization) \
                .filter(
                    (Organization.id == args.organization) \
                    | (Organization.short_name == args.organization) \
                    | (Organization.name == args.organization) \
                    | (Organization.code == args.organization)) \
                .one()
        except NoResultFound:
            message('No such organization identifiable with %s' % args.organization)
            return 1
        except MultipleResultsFound:
            message('Multiple organizations that match to %s' % args.organization)
            return 1

        try:
            events = []
            for event_id_or_code in args.event:
                try:
                    event = session.query(Event) \
                        .filter(Event.organization_id == organization.id) \
                        .filter(
                            (Event.id == event_id_or_code) \
                            | (Event.code == event_id_or_code)) \
                        .one()
                except NoResultFound:
                    message('No such event identifiable with %s' % event_id_or_code)
                    return 1
                except MultipleResultsFound:
                    message('Multiple events that match to %s' % event_id_or_code)
                    return 1
                events.append(event)

            for event in events:
                do_event_copy(
                    request,
                    session,
                    event
                    )
            transaction.commit()
        except ApplicationException as e:
            message(str(e))
            raise
    except:
        raise
    return 0

if __name__ == '__main__':
    sys.exit(main())

# vim: sts=4 sw=4 ts=4 et ai

