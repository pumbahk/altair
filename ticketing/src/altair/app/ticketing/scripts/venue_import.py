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
from altair.formhelpers.validators import JISX0208

io_encoding = locale.getpreferredencoding()

SVG_NAMESPACE = 'http://www.w3.org/2000/svg'
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

class ObjectRetriever(object):
    def __init__(self, doc):
        self.prototype_cache = {}
        self.doc = doc
        self.object_cache = {}

    def get_prototype(self, id):
        proto = self.prototype_cache.get(id)
        if proto is None:
            proto_node = self.doc.find('.//{%s}prototype[@id="%s"]' % (SITE_INFO_NAMESPACE, id))
            if proto_node is None:
                raise FormatError("Prototype %s not found" % id)

            proto = self.create_si_object_from_node(proto_node)
            self.prototype_cache[id] = proto
        return proto

    def create_si_object_from_node(self, node):
        object_ = {}
        id = node.get('id')
        if id is not None:
            self.object_cache[id] = object_

        proto_id = node.get('prototype')
        proto = self.get_prototype(proto_id) if proto_id is not None else None

        class_node = node.find('{%s}class' % SITE_INFO_NAMESPACE)
        if class_node is None:
            raise FormatError('<si:class> element does not exist under %s' % node)
        class_name = class_node.text

        if proto is not None:
            if proto['class'] != class_name:
                raise FormatError("the class name '%s' is not the same as that of the prototype '%s'" % class_name, proto['class']);
            props = dict(proto['properties'])
            colls = dict(proto['collections'])
        else:
            props = {}
            colls = {}

        for prop_node in node.findall('{%s}property' % SITE_INFO_NAMESPACE):
            ref_id = prop_node.get('refid')
            if ref_id is not None:
                object__ = self.object_cache[ref_id]
                props[prop_node.get('name')] = object__
            else:
                if prop_node.text is not None:
                    props[prop_node.get('name')] = unicode(prop_node.text)
                else:
                    props[prop_node.get('name')] = ''

        for coll_node in node.findall('{%s}collection' % SITE_INFO_NAMESPACE):
            coll = []
            for node_ in coll_node.findall('{%s}object' % SITE_INFO_NAMESPACE):
                coll.append(self.create_si_object_from_node(node_))
            colls[coll_node.get('name')] = coll

        object_['id'] = id
        object_['class'] = class_name
        object_['properties'] = props
        object_['collections'] = colls
        return object_

    def si_object_from_meta(self, node):
        metadata = node.findall('{%s}metadata' % SVG_NAMESPACE)
        if not metadata:
            return None

        obj = None

        for m in metadata:
            o = m.find('{%s}object' % SITE_INFO_NAMESPACE)
            if o is not None:
                if obj is not None:
                    raise FormatError("Multiple <si:object> present under the metadata elements of the same level")
                obj = self.create_si_object_from_node(o)
                obj['_node'] = node
                break

        return obj

    def retrieve_si_objects(self, nodes):
        retval = []
        for node in nodes:
            if not node.tag.startswith('{%s}' % SVG_NAMESPACE):
                continue
            obj = self.si_object_from_meta(node)
            child_objs = self.retrieve_si_objects(node.getchildren())
            if obj is not None:
                obj.setdefault('children', []).extend(child_objs)
                retval.append(obj)
            else:
                retval.extend(child_objs)
        return retval

    def __call__(self):
        self.check_error_chars()
        objects = self.retrieve_si_objects([self.doc.getroot()])
        if len(objects) == 0:
            raise FormatError("No object defined in the root metadata element")
        return self.retrieve_si_objects([self.doc.getroot()])[0]

    def check_error_chars(self):
        error_chars = set([ch for ch in self.generate_fail_characters()])
        if error_chars:
            raise ValidationError('Cannot use characters: {0}'.format(error_chars))

    def generate_fail_characters(self):
        root = self.doc.getroot()
        nodes = root.xpath('//si:object', namespaces={'si': SITE_INFO_NAMESPACE})
        for node in nodes:
            obj = self.create_si_object_from_node(node)            
            if obj['class'] in ('Block', 'Seat'):
                name = obj['properties']['name']
                for ch in JISX0208.generate_error_chars(name):
                    yield ch

def import_tree(registry, update, organization, tree, file, bundle_base_url=None, venue_id=None, max_adjacency=None):
    # 論理削除をインストールする都合でコードの先頭でセッションが初期化
    # されてほしくないので、ここで import する
    from altair.app.ticketing.models import DBSession
    from altair.app.ticketing.core.models import (
        Site,
        Venue,
        VenueArea,
        VenueArea_group_l0_id,
        Seat,
        SeatAttribute,
        SeatIndexType,
        SeatIndex,
        SeatAdjacencySet,
        SeatAdjacency
        )

    if tree['class'] != 'Venue':
        raise FormatError('The root object is not a Venue')

    backend_metadata_url = myurljoin(bundle_base_url, 'metadata.json')
    if update:
        site = Site(name=tree['properties']['name'], _backend_metadata_url=backend_metadata_url)
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
        venue.site.delete() # 論理削除
        venue.site = site
    else:
        site = Site(name=tree['properties']['name'], _backend_metadata_url=backend_metadata_url)
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
    seats_given = set()

    seat_names_given = set()

    if update:
        seats = dict((seat.l0_id, seat) for seat in venue.seats)
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
                    raise LogicalError("Dupliate seat_l0_id: %s" % seat_l0_id)
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

def import_or_update_svg(env, update, organization_name, file, bundle_base_url, venue_id, max_adjacency, dry_run):
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
    object_tree = ObjectRetriever(xmldoc)()
    try:
        import_tree(env['registry'], update, organization, object_tree, file, bundle_base_url, venue_id, max_adjacency)
        if dry_run:
            transaction.abort()
        else:
            transaction.commit()
    except:
        transaction.abort()
        raise
 
def main():
    parser = argparse.ArgumentParser(description='import venue data')
    parser.add_argument('config_uri', metavar='config', type=str, nargs=1,
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
    parsed_args = parser.parse_args()

    env = bootstrap(parsed_args.config_uri[0])

    if parsed_args.verbose:
        global verbose
        verbose = True

    site_base_url = env['registry'].settings.get('altair.site_data.backend_base_url', '')
    bundle_base_url = myurljoin(site_base_url, parsed_args.base_url)
    if bundle_base_url[-1] != '/':
        bundle_base_url += '/'
    for svg_file in parsed_args.svg_files:
        import_or_update_svg(
            env,
            update=parsed_args.update,
            organization_name=unicode(parsed_args.organization, io_encoding),
            file=svg_file,
            bundle_base_url=bundle_base_url,
            venue_id=parsed_args.venue,
            max_adjacency=parsed_args.max_adjacency,
            dry_run=parsed_args.dry_run)

if __name__ == '__main__':
    main()
