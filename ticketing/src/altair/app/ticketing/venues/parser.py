# encoding: utf-8

from altair.svg.constants import SVG_NAMESPACE
from altair.formhelpers.validators import JISX0208

SITE_INFO_NAMESPACE = 'http://xmlns.ticketstar.jp/2012/site-info'

class ObjectRetrieverError(Exception):
    pass

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
                raise ObjectRetrieverError("Prototype %s not found" % id)

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
            raise ObjectRetrieverError('<si:class> element does not exist under %s' % node)
        class_name = class_node.text

        if proto is not None:
            if proto['class'] != class_name:
                raise ObjectRetrieverError("the class name '%s' is not the same as that of the prototype '%s'" % class_name, proto['class']);
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
                    raise ObjectRetrieverError("Multiple <si:object> present under the metadata elements of the same level")
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
            raise ObjectRetrieverError("No object defined in the root metadata element")
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

