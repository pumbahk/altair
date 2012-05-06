from lxml import etree
import os
import sys
import transaction

from ticketing.models import DBSession
from ticketing.venues.models import Site, Venue, VenueArea, Seat, SeatAttribute

SVG_NAMESPACE = 'http://www.w3.org/2000/svg'
SITE_INFO_NAMESPACE = 'http://xmlns.ticketstar.jp/2012/site-info'

class FormatError(Exception):
    pass

class ObjectRetriever(object):
    def __init__(self, doc):
        self.prototype_cache = {}
        self.doc = doc

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
        else:
            props = {}

        for prop_node in node.findall('{%s}property' % SITE_INFO_NAMESPACE):
            props[prop_node.get('name')] = prop_node.text

        return {
            'class': class_name,
            'properties': props,
            }

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
                obj['id'] = node.get('id')
                break

        return obj

    def retrieve_si_objects(self, nodes):
        retval = []
        for node in nodes:
            if not node.tag.startswith('{%s}' % SVG_NAMESPACE):
                continue
            obj = self.si_object_from_meta(node)
            child_objs = self.retrieve_si_objects(node.getchildren())
            if child_objs:
                if obj is not None:
                    obj.setdefault('children', []).extend(child_objs)
                else:
                    retval.extend(child_objs)
            if obj is not None:
                retval.append(obj)
        return retval

    def __call__(self):
        return self.retrieve_si_objects([self.doc.getroot()])[0]

def import_tree(tree):
    if tree['class'] != 'Venue':
        raise FormatError('The root object is not a Venue')
    site = Site(name=tree['properties']['name'])
    venue = Venue(site=site, name=tree['properties']['name'])
    for block_obj in tree['children']:
        block = VenueArea(venue=venue, name=block_obj['properties']['name'])
        for row_obj in block_obj['children']:
            for seat_obj in row_obj['children']:
                seat = Seat(venue=venue, l0_id=seat_obj['id'])
                number = seat_obj['properties'].get('name')
                row = row_obj['properties'].get('name')
                gate = seat_obj['properties'].get('gate')
                floor = seat_obj['properties'].get('floor')
                if gate is not None:
                    seat['gate'] = gate
                if floor is not None:
                    seat['floor'] = floor
                if row is not None:
                    seat['row'] = row
                if number is not None:
                    seat['number'] = number
                seat.areas.append(block)
                DBSession.add(seat)
        DBSession.add(block)

    DBSession.add(site)
    DBSession.add(venue)

def import_svg(file):
    print 'Importing %s ...' % (file, )
    xmldoc = etree.parse(file)
    root = xmldoc.getroot()
    if root.tag != '{%s}svg' % SVG_NAMESPACE:
        raise FormatError("The document element is not a SVG root element")
    title = root.find('{%s}title' % SVG_NAMESPACE)
    print '  Title: %s' % title.text
    import_tree(ObjectRetriever(xmldoc)())
    transaction.commit()
 
def main(env, args):
    for arg in args:
        import_svg(arg)
