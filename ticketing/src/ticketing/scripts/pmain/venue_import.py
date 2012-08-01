from lxml import etree
import os
import sys
import transaction
import re
import argparse

from ticketing.models import DBSession
from ticketing.core.models import Site, Venue, VenueArea, VenueArea_group_l0_id, Seat, SeatAttribute, SeatIndexType, SeatIndex, Organization

SVG_NAMESPACE = 'http://www.w3.org/2000/svg'
SITE_INFO_NAMESPACE = 'http://xmlns.ticketstar.jp/2012/site-info'

class FormatError(Exception):
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
                props[prop_node.get('name')] = prop_node.text

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
        objects = self.retrieve_si_objects([self.doc.getroot()])
        if len(objects) == 0:
            raise FormatError("No object defined in the root metadata element")
        return self.retrieve_si_objects([self.doc.getroot()])[0]

def import_tree(organization, tree, file):
    if tree['class'] != 'Venue':
        raise FormatError('The root object is not a Venue')
    site = Site(name=tree['properties']['name'], drawing_url='file:'+file)
    venue = Venue(site=site, name=tree['properties']['name'])
    venue.organization = organization
    seat_index_type_objs = tree['collections'].get('seatIndexTypes')
    seat_index_type_map = {}
    if seat_index_type_objs is not None:
        for seat_index_type_obj in seat_index_type_objs:
            if seat_index_type_obj['class'] != 'SeatIndexType':
                raise FormatError('Any object in seatIndexTypes must be a SeatIndexType')
            seat_index_type = SeatIndexType(venue=venue, name=seat_index_type_obj['properties']['name'])
            seat_index_type_map[seat_index_type_obj['id']] = seat_index_type
            venue.seat_index_types.append(seat_index_type)
           
    for block_obj in tree['children']:
        block = VenueArea(name=block_obj['properties']['name'])
        group_l0_id = block_obj['_node'].get('id')
        if group_l0_id is not None:
            DBSession.add(VenueArea_group_l0_id(area=block, venue=venue, group_l0_id=group_l0_id))
        for row_obj in block_obj['children']:
            row_name = row_obj['properties'].get('name')
            for seat_obj in row_obj['children']:
                seat = Seat(venue=venue, l0_id=seat_obj['_node'].get('id'), group_l0_id=group_l0_id)
                name = seat_obj['properties'].get('name')
                gate = seat_obj['properties'].get('gate')
                floor = seat_obj['properties'].get('floor')
                indexes = seat_obj['collections'].get('indexes')
                if name is not None:
                    seat.name = name
                if row_name is not None:
                    seat['row'] = row_name
                if gate is not None:
                    seat['gate'] = gate
                if floor is not None:
                    seat['floor'] = floor
                if indexes is not None:
                    for index_obj in indexes:
                        DBSession.add(
                            SeatIndex(
                                seat=seat,
                                index=index_obj['properties']['index'],
                                seat_index_type=seat_index_type_map[index_obj['properties']['index_type']['id']]))
                DBSession.add(seat)
        DBSession.add(block)

    DBSession.add(site)
    DBSession.add(venue)

def import_svg(organization_name, file):
    organization = DBSession.query(Organization).filter_by(name=organization_name).one()
    print 'Importing %s for %s...' % (file, organization_name)
    xmldoc = etree.parse(file)
    root = xmldoc.getroot()
    if root.tag != '{%s}svg' % SVG_NAMESPACE:
        raise FormatError("The document element is not a SVG root element")
    title = root.find('{%s}title' % SVG_NAMESPACE)
    print '  Title: %s' % title.text
    import_tree(organization, ObjectRetriever(xmldoc)(), file)
    transaction.commit()
 
def main(env, args):
    parser = argparse.ArgumentParser(description='import venue data')
    parser.add_argument('svg_files', metavar='svg', type=str, nargs='+',
                        help='an svg file')
    parser.add_argument('-O', '--organization', metavar='organization',
                        help='organization name')
    parsed_args = parser.parse_args(args)
    for svg_file in parsed_args.svg_files:
        import_svg(parsed_args.organization, svg_file)
