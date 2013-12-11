#!/usr/bin/env python
# encoding: utf-8
from lxml import etree
import os
import sys
import transaction
import re
import argparse
import locale
import time
import json
import gzip
import csv

from cStringIO import StringIO

from pyramid.paster import get_app, bootstrap, setup_logging

from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

from altair.pyramid_assets import get_resolver
from altair.pyramid_assets.interfaces import IWritableAssetDescriptor

from altair.app.ticketing.utils import myurljoin
from altair.formhelpers.validators import JISX0208

from altair.svg.reader import Scanner, VisitorBase
from altair.svg.constants import SVG_NAMESPACE
from altair.svg import geometry as geom

io_encoding = locale.getpreferredencoding()

verbose = False

class FormatError(Exception):
    pass

class LogicalError(Exception):
    pass

class ValidationError(Exception):
    pass

def message(text):
    sys.stderr.write(text.encode(io_encoding))
    sys.stderr.write('\n')
    sys.stderr.flush()

def relativate(a, b):
    a = os.path.normpath(a)
    b = os.path.normpath(b)
    abs_a = os.path.abspath(a)
    abs_b = os.path.abspath(b)
    pfx = os.path.commonprefix([abs_a, abs_b])
    rest_a = abs_a[len(pfx):].lstrip('/')
    if rest_a:
        return re.sub(r'[^/]+(?=/|$)', '..', rest_a) + abs_b[len(pfx):]
    else:
        return abs_b[len(pfx) + 1:]

class Visitor(VisitorBase):
    def __init__(self):
        self.transform = geom.I
        self.result = {}

    def decorate_transform(self, fn):
        def _(scanner, n):
            prev_transform = self.transform
            transform_str = n.get('transform')
            if transform_str:
                transform = geom.parse_transform(transform_str)
                # do not rewrite this like tfm *= tfm
                # as the expression mutates the LHS matrix!
                self.transform = self.transform * transform
            fn(scanner, n)
            self.transform = prev_transform
        return _

    def visit_svg(self, scanner, n):
        scanner(n)

    def visit_g(self, scanner, n):
        scanner(n)

    def visit_rect(self, scanner, n):
        self._handle(
            n,
            (
                geom.as_user_unit(n.get('x', u'0')) + geom.as_user_unit(n.get('width', u'0')) / 2,
                geom.as_user_unit(n.get('y', u'0')) + geom.as_user_unit(n.get('height', u'0')) / 2
                )
            )

    def visit_circle(self, scanner, n):
        r = geom.as_user_unit(n.get('r', u'0'))
        self._handle(
            n,
            (
                geom.as_user_unit(n.get('cx', u'0')) + r,
                geom.as_user_unit(n.get('cy', u'0')) + r
                )
            )

    def visit_ellipse(self, scanner, n):
        self._handle(
            n,
            (
                geom.as_user_unit(n.get('cx', u'0')) + geom.as_user_unit(n.get('rx', u'0')),
                geom.as_user_unit(n.get('cy', u'0')) + geom.as_user_unit(n.get('ry', u'0'))
                )
            )

    def _handle(self, n, pos):
        id_ = n.get('id')
        if id_ is None:
            return
        pos = (self.transform * [[pos[0]], [pos[1]], [1.]]).getA()[(0, 1), 0]
        self.result[id_] = (n, pos)

def get_positions(xmldoc):
    visitor = Visitor()
    Scanner(visitor)([xmldoc.getroot()])
    return visitor.result

def import_tree(registry, metadata_file, bundle_base_url, site_id, dump=False, no_upload=False, no_update=False, dry_run=False):
    # 論理削除をインストールする都合でコードの先頭でセッションが初期化
    # されてほしくないので、ここで import する
    from altair.app.ticketing.models import DBSession
    from altair.app.ticketing.core.models import (
        Site,
        L0Seat,
        )

    site_q = DBSession.query(Site)
    try:
        site_q = site_q.filter_by(id=site_id)
        site = site_q.one()
    except NoResultFound:
        message("No such venue")
        return
    except MultipleResultsFound:
        message("More than one venues with the same name found; venue_id (--venue) needs to be given in order to specify the venue")
        return

    frontend_metadata = json.load(open(metadata_file))
    base_dir = os.path.dirname(metadata_file)

    pages = frontend_metadata['pages']

    l0_seats = {}
    for l0_seat in DBSession.query(L0Seat).filter_by(site_id=site.id):
        l0_seats[l0_seat.l0_id] = l0_seat
    positions = {}
    for filename, data in pages.items():
        path_to_svg = os.path.join(base_dir, filename)
        message('Reading %s...' % path_to_svg)
        name_part, ext = os.path.splitext(filename)
        ext = ext.lower()
        if ext == '.svg':
            svg_file = open(path_to_svg)
        elif ext == '.svgz':
            svg_file = gzip.open(path_to_svg, 'r')
        else:
            raise FormatError('unsupported file extension: %s' % ext)
        xmldoc = etree.parse(svg_file)
        positions_in_xml = get_positions(xmldoc)
        l0_ids_in_xml = set(positions_in_xml).intersection(l0_seats)
        message('number of seats in the file: %d' % len(l0_ids_in_xml))
        intersection = l0_ids_in_xml.intersection(positions)
        if intersection:
            message_text = 'the following l0_ids are found duplicate: %s' % ', '.join(intersection)
            if no_update:
                message(message_text)
            else:
                raise ValidationError(message_text)
        if dump:
            w = csv.writer(sys.stdout)
            for l0_id in l0_ids_in_xml:
                n, position = positions_in_xml[l0_id]
                l0_seat = l0_seats[l0_id]
                w.writerow([col.encode('utf-8') for col in [
                    l0_id,
                    l0_seat.gate_name or u'',
                    l0_seat.floor_name or u'',
                    l0_seat.block_name or u'',
                    l0_seat.row_no or u'',
                    l0_seat.seat_no or u'',
                    l0_seat.name or u'',
                    u'%g' % position[0],
                    u'%g' % position[1],
                    ]])

        positions.update(positions_in_xml)

    if not no_upload:
        resolver = get_resolver(registry)
        uploaded = True
        new_pages = {}
        for filename, data in pages.items():
            path_to_svg = os.path.join(base_dir, filename)
            name_part, ext = os.path.splitext(filename)
            ext = ext.lower()
            if ext == '.svg':
                uploaded_filename = '%s.svgz' % name_part
                svg_file = open(path_to_svg)
                gzipped = StringIO()
                shutil.copyfileobj(svg_file, gzip.GzipFile(mode='w', fileobj=io))
                svg_file.seek(0) 
            elif ext == '.svgz':
                uploaded_filename = filename
                gzipped = open(path_to_svg)
                svg_file = gzip.GzipFile(mode='r', fileobj=gzipped)
            try:
                new_pages[uploaded_filename] = data
                drawing_url = myurljoin(bundle_base_url, uploaded_filename)
                drawing_asset = resolver.resolve(drawing_url)
                if IWritableAssetDescriptor.providedBy(drawing_asset):
                    message('Uploading %s...' % drawing_url)
                    if not dry_run:
                        gzipped.seek(0)
                        drawing_asset.write(gzipped.read())
                else:
                    uploaded = False
            finally:
                svg_file.close()
                gzipped.close()

        frontend_metadata_url = myurljoin(bundle_base_url, 'metadata.json')
        metadata_asset = resolver.resolve(frontend_metadata_url)
        if IWritableAssetDescriptor.providedBy(metadata_asset):
            message('Uploading %s...' % frontend_metadata_url)
            if not dry_run:
                metadata_asset.write(json.dumps(frontend_metadata, encoding='utf-8'))
        else:
            uploaded = False
        if not no_update:
            site._frontend_metadata_url = frontend_metadata_url

        if not uploaded:
            message('WARNING: Drawing was not uploaded automatically')

def import_or_update_svg(env, metadata_file, bundle_base_url, site_id, dump, no_upload, no_update, dry_run):
    from altair.app.ticketing.models import DBSession
    from altair.app.ticketing.core.models import Organization
    message('Processing %s...' % (metadata_file, ))
    try:
        import_tree(env['registry'], metadata_file, bundle_base_url, site_id, dump, no_upload, dry_run)
        if dry_run:
            transaction.abort()
        else:
            transaction.commit()
    except:
        transaction.abort()
        raise
 
def main():
    parser = argparse.ArgumentParser(description='import venue data')
    parser.add_argument('config_uri', metavar='config', type=str,
                        help='config file')
    parser.add_argument('metadata_file', metavar='metadata',
                        help='a frontend metadata json file')
    parser.add_argument('-n', '--dry-run', action='store_true',
                        help='show what would have been done')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='verbose mode')
    parser.add_argument('-s', '--site', metavar='site-id',
                        required=True, help='specify site id (use with -u)')
    parser.add_argument('-U', '--base-url', metavar='base_url',
                        help='base url under which the site data will be put')
    parser.add_argument('--no-upload', action='store_true',
                        help='do not perform uploading')
    parser.add_argument('--no-update', action='store_true',
                        help='do not perform updating database')
    parser.add_argument('--dump', action='store_true',
                        help='dump seat positions')
    parsed_args = parser.parse_args()

    setup_logging(parsed_args.config_uri)
    env = bootstrap(parsed_args.config_uri)

    if parsed_args.verbose:
        global verbose
        verbose = True

    site_base_url = env['registry'].settings.get('altair.site_data.frontend_base_url', '')
    bundle_base_url = myurljoin(site_base_url, parsed_args.base_url)
    if bundle_base_url[-1] != '/':
        bundle_base_url += '/'
    import_or_update_svg(
        env,
        metadata_file=parsed_args.metadata_file,
        bundle_base_url=bundle_base_url,
        site_id=parsed_args.site,
        dump=parsed_args.dump,
        no_upload=parsed_args.no_upload,
        no_update=parsed_args.no_update,
        dry_run=parsed_args.dry_run)

if __name__ == '__main__':
    main()
