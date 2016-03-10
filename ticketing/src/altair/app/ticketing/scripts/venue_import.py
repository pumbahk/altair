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

from pyramid.paster import get_app, bootstrap

from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

from altair.pyramid_assets import get_resolver
from altair.pyramid_assets.interfaces import IWritableAssetDescriptor

from altair.app.ticketing.utils import myurljoin

from altair.svg.constants import SVG_NAMESPACE

from altair.app.ticketing.venues.parser import ObjectRetriever

io_encoding = locale.getpreferredencoding()

SITE_INFO_NAMESPACE = 'http://xmlns.ticketstar.jp/2012/site-info'

verbose = False

class FormatError(Exception):
    pass

class LogicalError(Exception):
    pass

class ValidationError(Exception):
    pass

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

def import_tree(registry, update, organization, xmldoc, file, bundle_base_url=None, venue_id=None, max_adjacency=None, prefecture=u'全国'):
    # 論理削除をインストールする都合でコードの先頭でセッションが初期化
    # されてほしくないので、ここで import する
    from altair.app.ticketing.models import DBSession
    from altair.app.ticketing.core.models import (
        SiteProfile,
        Site,
        Venue,
        VenueArea,
        VenueArea_group_l0_id,
        Seat,
        SeatAttribute,
        SeatIndexType,
        SeatIndex,
        SeatAdjacencySet,
        SeatAdjacency,
        L0Seat,
        )

    tree = ObjectRetriever(xmldoc)()
    if tree['class'] != 'Venue':
        raise FormatError('The root object is not a Venue')

    backend_metadata_url = myurljoin(bundle_base_url, 'metadata.json')
    siteprofile = SiteProfile(name = tree['properties']['name'], prefecture = prefecture)
    if update:
        site = Site(name=tree['properties']['name'], _backend_metadata_url=backend_metadata_url, siteprofile = siteprofile)
        venue_q = DBSession.query(Venue)
        if venue_id is not None:
            venue_q = venue_q.filter_by(organization=organization, id=venue_id)
        else:
            venue_q = venue_q.filter_by(organization=organization, name=tree['properties']['name'])
        try:
            venue = venue_q.one()
        except NoResultFound:
            print "No such venue"
            return
        except MultipleResultsFound:
            print "More than one venues with the same name found; venue_id (--venue) needs to be given in order to specify the venue"
            return
        l0_seats = dict((l0_seat.l0_id, l0_seat) for l0_seat in DBSession.query(L0Seat).filter_by(site_id=venue.site.id))
        venue.site.delete() # 論理削除
        venue.site = site
    else:
        site = Site(name=tree['properties']['name'], _backend_metadata_url=backend_metadata_url, siteprofile = siteprofile)
        l0_seats = dict()
        venue = Venue(site=site, name=tree['properties']['name'])
        venue.organization = organization

    seat_index_type_objs = tree['collections'].get('seatIndexTypes')
    seat_index_type_map = {}
    adjacency_sets = {}

    if seat_index_type_objs is not None:
        if update:
            seat_index_types = venue.seat_index_types
        else:
            seat_index_types = []

        seat_index_type_obj_map = {}
        new_seat_index_type_objs = []

        for seat_index_type_obj in seat_index_type_objs:
            if seat_index_type_obj['class'] != 'SeatIndexType':
                raise FormatError('Any object in seatIndexTypes must be a SeatIndexType')
            seat_index_type_obj_map[seat_index_type_obj['properties']['name']] = seat_index_type_obj

            # 既存の SeatIndexType と合致するものがないかを調べる
            for seat_index_type in seat_index_types:
                if seat_index_type.name == seat_index_type_obj['properties']['name']:
                    # 合致する物があれば、seat_index_type_map に
                    # id - seat_index_type の関連づけを入れる
                    seat_index_type_map[seat_index_type_obj['id']] = seat_index_type
                    break
            else:
                # 合致する物がないので、new_seat_index_type_objs に
                # seat_index_type_obj を入れて、後でまとめて追加処理をする
                new_seat_index_type_objs.append(seat_index_type_obj)

        # 既存の SeatIndexType と合致するものがないかを調べる
        for seat_index_type in seat_index_types:
            seat_index_type_obj = seat_index_type_obj_map.get(seat_index_type.name)
            if seat_index_type_obj is None:
                # なければ既存のやつを削除する
                print '[DELETE] SeatIndexType(id=%d)' % seat_index_type.id
                seat_index_type.delete()
            else:
                # あれば、紐づいている SeatIndex を削除しておく
                # (あとで追加されるので)
                print '[UPDATE] SeatIndexType(id=%d)' % seat_index_type.id
                for seat_index in DBSession.query(SeatIndex).filter_by(seat_index_type=seat_index_type):
                    # 論理削除したいのでループ
                    seat_index.delete()

        # new_seat_index_type_objs に入っているものに対応する SeatIndexType
        # を作る
        for seat_index_type_obj in new_seat_index_type_objs:
            print (u'[ADD] SeatIndexType(name="%s")' % seat_index_type_obj['properties']['name']).encode(io_encoding)
            seat_index_type = SeatIndexType(venue=venue, name=seat_index_type_obj['properties']['name'])
            venue.seat_index_types.append(seat_index_type)
            seat_index_type_map[seat_index_type_obj['id']] = seat_index_type

    if update:
        venue_areas = venue.areas
    else:
        venue_areas = []

    new_blocks = []

    # 連席情報をクリア
    for _set in DBSession.query(SeatAdjacencySet).filter_by(site=venue.site):
        # 論理削除したいのでループ
        _set.delete()

    new_seat_count = 0
    deleted_seat_count = 0
    updated_seat_count = 0
    seats_given = set()

    seat_names_given = set()

    if update:
        seats = dict((seat.l0_id, seat) for seat in venue.seats)
        if len(l0_seats) != len(seats):
            raise ValidationError("ERROR: Number of existing l0 seats doesn't match to that of existing seats")
        print 'Number of existing seats: %d' % len(seats)
    else:
        seats = dict()

    for block_obj in tree['children']:
        t_start = time.time()
        num_seats_in_block = 0
        for venue_area in venue_areas:
            if venue_area.name == block_obj['properties']['name']:
                block = venue_area
                break
        else:
            print (u'[ADD] VenueArea(name="%s",id="%s")' % (block_obj['properties']['name'], block_obj['_node'].get('id'))).encode(io_encoding)
            block = VenueArea(name=block_obj['properties']['name'])
            new_blocks.append(block)

        group_l0_id = block_obj['_node'].get('id')
        if group_l0_id is not None:
            for group in block.groups:
                if group.group_l0_id == group_l0_id:
                    break
            else:
                # 論理削除の必要なし
                DBSession.query(VenueArea_group_l0_id).filter_by(venue=venue, group_l0_id=group_l0_id).delete()
                DBSession.add(VenueArea_group_l0_id(area=block, venue=venue, group_l0_id=group_l0_id))

        for row_obj in block_obj['children']:
            row_l0_id = row_obj['_node'].get('id')
            if verbose:
                print "  - row: %s" % row_l0_id
            row_name = row_obj['properties'].get('name')
            seat_objs = row_obj['children']
            num_seats_in_row = len(seat_objs)
            num_seats_in_block += num_seats_in_row
            seats_in_row = []
            seat_order = dict()
            for seat_obj in seat_objs:
                seat_l0_id = seat_obj['_node'].get('id')
                if seat_l0_id in seats_given:
                    # id重複
                    raise LogicalError("Duplicate seat_l0_id: %s" % seat_l0_id)
                seats_given.add(seat_l0_id)
                seat = seats.get(seat_l0_id)
                if seat is None:
                    seat = Seat(venue=venue, l0_id=seat_l0_id, group_l0_id=group_l0_id, row_l0_id=row_l0_id)
                    DBSession.add(seat)
                    if update:
                        print '[ADD] Seat(l0_id=%s)' % seat.l0_id
                    new_seat_count += 1
                name = seat_obj['properties'].get('name')
                if name in seat_names_given:
                    # name重複
                    raise LogicalError("Dupliate seat name: %s" % name)
                seat_names_given.add(name)
                seat_no = seat_obj['properties'].get('seat_no')
                gate = seat_obj['properties'].get('gate')
                floor = seat_obj['properties'].get('floor')
                indexes = seat_obj['collections'].get('indexes')
                seat_index = seat_obj['properties'].get('seat_index')

                old_l0_seat = l0_seats.get(seat_l0_id)
                if not old_l0_seat is None:
                    if old_l0_seat.name != name or \
                        old_l0_seat.row_l0_id != row_l0_id or \
                        old_l0_seat.group_l0_id != group_l0_id or \
                        old_l0_seat.seat_no != seat_no or \
                        old_l0_seat.row_no != row_name or \
                        old_l0_seat.block_name != block.name or \
                        old_l0_seat.floor_name != floor or \
                        old_l0_seat.gate_name != gate:
                        print '[UPDATE] Seat(l0_id=%s)' % seat.l0_id
                        updated_seat_count += 1

                l0_seat = L0Seat(
                    site_id=site.id,
                    l0_id=seat_l0_id,
                    row_l0_id=row_l0_id,
                    group_l0_id=group_l0_id,
                    name=name,
                    seat_no=seat_no,
                    row_no=row_name,
                    block_name=block.name,
                    floor_name=floor,
                    gate_name=gate
                    )
                DBSession.add(l0_seat)

                if seat_index is not None:
                    seat_order[seat_l0_id] = int(seat_index)    # for build adjacencies
                if name is not None:
                    seat.name = name
                if seat_no is not None:
                    seat.seat_no = seat_no
                if row_name is not None:
                    seat['row'] = row_name
                if gate is not None:
                    seat['gate'] = gate
                if floor is not None:
                    seat['floor'] = floor
                if indexes is not None:
                    for index_obj in indexes:
                        seat_index_type = seat_index_type_map[index_obj['properties']['index_type']['id']]
                        index = index_obj['properties']['index']
                        try:
                            seat_index = SeatIndex.query.filter_by(seat_index_type=seat_index_type, seat_id=seat.id).one()
                        except NoResultFound:
                            seat_index = SeatIndex(seat=seat, seat_index_type=seat_index_type)
                            DBSession.add(seat_index)
                        seat_index.index = index
                seats_in_row.append(seat)

            if seats_in_row[0].l0_id in seat_order:
                # sort by index
                seats_in_row.sort(key=lambda a: seat_order[a.l0_id])
            else:
                # sort by l0_id
                seats_in_row.sort(lambda a, b: cmp(a.l0_id, b.l0_id))

            # generate adjacencies
            for seat_count in range(2, (min(num_seats_in_row, max_adjacency) if max_adjacency else num_seats_in_row) + 1):
                adjacency_set = adjacency_sets.get(seat_count)
                if adjacency_set is None:
                    adjacency_set = adjacency_sets[seat_count] = SeatAdjacencySet(site=venue.site, seat_count=seat_count)
                adjacency_set.adjacencies.extend(
                    SeatAdjacency(seats=seats_in_row[i:i + seat_count])
                    for i in range(0, num_seats_in_row - seat_count + 1))
        DBSession.add(block)

        print "  This block contains %u seats, takes %.2f sec." % (num_seats_in_block, time.time()-t_start)

    seats_to_be_deleted = set(seats) - seats_given
    for seat_l0_id in seats_to_be_deleted:
        seat = seats.get(seat_l0_id)
        print '[DELETE] Seat(id=%d)' % seat.id
        seat.delete() # 論理削除

    print 'Number of seats to be added: %d' % new_seat_count
    print 'Number of seats to be updated: %d' % updated_seat_count 
    print 'Number of seats to be deleted: %d' % len(seats_to_be_deleted)

    for venue_area in venue_areas:
        for block_obj in tree['children']:
            if venue_area.name == block_obj['properties']['name']:
                break
        else:
            print '[DELETE] VenueArea(id=%d)' % venue_area.id
            venue_area.delete()

    for adjacency_set in adjacency_sets.values():
        print '[ADD] SeatAdjacencySet(seat_count=%d)' % adjacency_set.seat_count
        DBSession.add(adjacency_set)

    DBSession.merge(siteprofile)
    DBSession.merge(site)
    DBSession.merge(venue)

    resolver = get_resolver(registry)
    metadata = resolver.resolve(backend_metadata_url)
    drawing = resolver.resolve(myurljoin(bundle_base_url, 'root.svg'))
    if IWritableAssetDescriptor.providedBy(metadata) and IWritableAssetDescriptor.providedBy(drawing):
        drawing.write(open(file).read())
        metadata.write(json.dumps(dict(pages={'root.svg':{}}), encoding='utf-8'))
    else:
        print 'WARNING: Drawing was not uploaded automatically'

def import_or_update_svg(env, update, organization_name, file, bundle_base_url, venue_id, max_adjacency, dry_run, prefecture):
    from altair.app.ticketing.models import DBSession
    from altair.app.ticketing.core.models import Organization
    organization = DBSession.query(Organization).filter_by(name=organization_name).one()
    print 'Importing %s for %s...' % (file, organization_name.encode(io_encoding))
    xmldoc = etree.parse(file)
    root = xmldoc.getroot()
    if root.tag != '{%s}svg' % SVG_NAMESPACE:
        raise FormatError("The document element is not a SVG root element")
    title = root.find('{%s}title' % SVG_NAMESPACE)
    print '  Title: %s' % title.text.encode(io_encoding)
    try:
        import_tree(env['registry'], update, organization, xmldoc, file, bundle_base_url, venue_id, max_adjacency, prefecture)
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
    parser.add_argument('svg_files', metavar='svg', type=str, nargs='+',
                        help='an svg file')
    parser.add_argument('-O', '--organization', metavar='organization',
                        required=True, help='organization name')
    parser.add_argument('-u', '--update', action='store_true',
                        help='update existing data')
    parser.add_argument('-A', '--max-adjacency', type=int,
                        help='max adjacency')
    parser.add_argument('-n', '--dry-run', action='store_true',
                        help='show what would have been done')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='verbose mode')
    parser.add_argument('--venue', metavar='venue-id',
                        help='specify venue id (use with -u)')
    parser.add_argument('-U', '--base-url', metavar='base_url',
                        help='base url under which the site data will be put')
    parser.add_argument('-P', '--prefecture', metavar='prefecture',
                        help='prefecture to be set on site and siteprofile')
    parsed_args = parser.parse_args()

    env = bootstrap(parsed_args.config_uri)

    if parsed_args.verbose:
        global verbose
        verbose = True

    site_base_url = env['registry'].settings.get('altair.site_data.backend_base_url', '')
    bundle_base_url = myurljoin(site_base_url, parsed_args.base_url)
    if bundle_base_url[-1] != '/':
        bundle_base_url += '/'
    hex_prefecture = parsed_args.prefecture
    prefecture = hex_prefecture.decode('hex')
    for svg_file in parsed_args.svg_files:
        import_or_update_svg(
            env,
            update=parsed_args.update,
            organization_name=unicode(parsed_args.organization, io_encoding),
            file=svg_file,
            bundle_base_url=bundle_base_url,
            venue_id=parsed_args.venue,
            max_adjacency=parsed_args.max_adjacency,
            dry_run=parsed_args.dry_run,
            prefecture=prefecture)

if __name__ == '__main__':
    main()
