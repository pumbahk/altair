#!/usr/bin/env python -S
# -*- coding: utf-8 -*-
import sys
import re
import os
import xml.sax
import io
import StringIO
from xml.sax.saxutils import escape

reload(sys)
sys.setdefaultencoding('utf-8')

xmlns = {
    "xmlns":                                       "xmlns",
    "http://www.w3.org/2000/svg":                  "svg",
    "http://xmlns.ticketstar.jp/2012/site-info":   "si",
    "http://www.w3.org/1999/02/22-rdf-syntax-ns#": "rdf",
    "http://purl.org/dc/elements/1.1/":            "dc"
}

shape_tags = set(["path", "rect", "circle", "text"])

class Printer():

    def __init__(self,  output=sys.stdout, indent=2, header="", output_file_append=False):
        self.setOutput(output)
        self.output_file_append = output_file_append
        self.indent = indent
        self.indent_space = ' '*self.indent
        self.pretty_print = (self.indent != False) and (self.indent > -1);
        self.header = header

    def setOutput(self, output=None):
        if output == None:
            self.output_type  = "s" # string
        elif isinstance(output, (file, StringIO.StringIO, io.StringIO)):
            self.output_type  = "i" # io_stream
        elif isinstance(output, (str, basestring)):
            self.output_type  = "f" # file
        else:
            raise TypeError("The specified 'output' type is not surported.")

        self.output           = output

    def printHeader(self):
        self.output.write(self.header)

    def printIndent(self, depth):
        if self.pretty_print:
            self.output.write ( "\n" )
            self.output.write (self.indent_space * depth)

    def print_all(self, root):

        def iter (elem, depth, last_of_list):

            if isinstance(elem, Element):

                self.printIndent(depth)

                self.output.write("<")

                if elem.getNamespace() != None and xmlns.has_key(elem.getNamespace()):
                    ns = xmlns[elem.getNamespace()]
                    self.output.write(ns)
                    self.output.write(":")

                self.output.write(elem.getTagName())

                for k, v in elem.getAttribute().src.iteritems():
                    self.output.write(" ")

                    if k[0] != None and xmlns.has_key(k[0]):
                        ns = xmlns[k[0]]
                        self.output.write(ns)
                        self.output.write(":")

                    self.output.write(k[1])
                    self.output.write("=")
                    self.output.write("\"")
                    self.output.write(escape(v))
                    self.output.write("\"")
                self.output.write(">")

                children = elem.getChildren()
                leng     = len(children)
                for child in children:
                    leng-=1
                    iter(child, depth+1, leng == 0)

                self.output.write("</")

                if elem.getNamespace() != None and xmlns.has_key(elem.getNamespace()):
                    ns = xmlns[elem.getNamespace()]
                    self.output.write(ns)
                    self.output.write(":")

                self.output.write(elem.getTagName())
                self.output.write(">")

                if last_of_list:
                    self.printIndent(depth-1)

            else:
                self.output.write(escape(elem))

        self.printHeader()

        for k, v in xmlns.iteritems():
            if (k != "xmlns"):
                root.getAttribute().put(v, k, "xmlns")

        iter(root, 0, True)

        if self.pretty_print:
            self.output.write("\n")


    def pr(self, data):
        if self.output_type == "s": #string
            try:
                o = StringIO.StringIO()
                self.setOutput(o)
                self.print_all(data)
                c = o.getvalue()
            finally:
                o.close()
            return c

        if self.output_type == "f":
            if self.output_file_append:
                mode = 'a'
            else:
                mode = 'w'

            with file(self.output, mode) as f:
                self.setOutput(f)
                self.print_all(data)

            return

        self.print_all(data)


class Element():

    def __init__(self, name, attributes=None, namespace=None):
        self.name = name
        self.attribute = Attributes(attributes)
        self.namespace = namespace
        self.children  = []

    def getNamespace(self):
        return self.namespace

    def getTagName(self):
        return self.name

    def getAttribute(self):
        return self.attribute

    def getChildren(self):
        return self.children

    def getFirstChild(self):
        return self.children[0] if len(self.children) > 0 else None

    def hasChild(self):
        return len(self.children) > 0

    def appendChild(self, *children):
        for c in children:
            self.children.append(c)

    def removeChild(self, *children):
        for c in children:
            i = 0
            for mc in self.children:
                if mc == c:
                    self.children.pop(i)
                i+=1
        return children

    def replaceChild(self, child, new_child=None):
        if new_child == None:
            return self.removeChild(child)

        i = 0

        for mc in self.children:
            if mc == child:
                self.children[i] = new_child
            i+=1

        return child

class Attributes():

    def __init__(self, src=None):
        self.src = {}
        if src != None:
            for key in src.getNames():
                value = src.getValue(key)
                self.put(key[1], value, key[0])


    def get(self, key, ns=None):
        if ns == None:
            for k, v in self.src.iteritems():
                if (k[1] == key):
                    return v
            return None
        return self.src[ns,key] if self.src.has_key(ns,key) else None

    def put(self, key, value, ns=None):
        self.src[ns,key] = value


class Reader():

    class ReaderContentHandler(xml.sax.handler.ContentHandler):

        def __init__(self):
            self.last_called = "__init__"

        def startDocument(self):
            self.root  = Element('root')
            self.stack = [self.root]
            self.node  = []

        def endDocument(self):
            pass

        def characters(self, content):
            if not re.match('^\s*$', content):
                self.node.appendChild(content)

        def startElementNS(self, name, qname, attr):
            self.parent = self.stack[-1]
            self.node   = Element(name[1], attr, name[0])
            self.parent.appendChild(self.node)
            self.stack.append(self.node)


        def endElementNS(self, name, qname):
            self.stack.pop()


    def __init__( self, input=None, input_string=None):

        self.reader = xml.sax.make_parser()
        self.reader.setFeature(xml.sax.handler.feature_namespaces, True)

        self.handler = self.ReaderContentHandler()
        self.reader.setContentHandler(self.handler)

        if input != None:
            self.set_input(input)
        else:
            self.set_input_string(input_string or "")

    def set_input(self, input):
        if isinstance(input, file):
            self.input_type = "i"
        elif isinstance(input, (str, basestring)):
            self.input_type = "f"
        elif isinstance(input, (StringIO.StringIO, io.StringIO)):
            self.set_input_string(input.getvalue())
            return
        else:
            raise TypeError("The specified 'input' type is not surported.")

        self.input        = input

    def set_input_string(self, input_string):
        if isinstance(input_string, (str, basestring)):
            self.input_type = "s"
        else:
            raise TypeError("The specified value is not a string.")

        self.input_string = input_string

    def read_string(self, string = None):
        self.reader.parseString(string or self.input_string)
        return self.handler.root.getFirstChild()

    def read_stream(self, stream = None):
        self.reader.parse(stream or self.input)
        return self.handler.root.getFirstChild()

    def read_file(self, path = None):
        with file((path or self.input), 'r') as f:
            self.reader.parse(f)
        return self.handler.root.getFirstChild()

    def read(self):
        if(self.input_type == "s"): # string
            return self.read_string()
        if(self.input_type == "i"): # io_stream
            return self.read_stream()
        if(self.input_type == "f"): # file
            return self.read_file()
        else:
            raise StandardError("input_type is unknown type. -> '"+self.input_type+"' .")


class Metadata():

    prototypeTable = {}

    def __init__(self, tag_name, class_name, my_id, proto_id):

        self.src = {}

        self.name = tag_name
        self.klass = class_name

        self.prototype = Metadata.prototypeTable[proto_id] if proto_id != None else None

        if my_id != None:
            Metadata.prototypeTable[my_id] = self

    def prototype_p(self):
        return self.name == "prototype"

    def getClassName(self):
        return self.klass

    def setClassName(self, klass):
        self.klass = klass
        return klass

    def getProperties(self):
        if self.prototype != None:
            return dict( self.prototype.getProperties().items() + self.src.items() )

        return self.src

    def getValue(self, propKey):
        if self.src.has_key(propKey):
            return self.src[propKey]
        return self.prototype.getValue(propKey) if self.prototype != None else None

    def setValue(self, propKey, value):
        self.src[propKey] = value
        return value


class Metadatas():
    def __init__(self):
        self.stack = []

    def getClassNames(self):
        return map(lambda x: x.getClassName(), self.stack)

    def getProperties(self):
        rt = {}
        for s in reversed(self.stack):
            className = s.getClassName()
            if rt.has_key(className):
                for k, v in s.getProperties():
                    rt[className][k] = v
            else:
                rt[className] = s.getProperties()
        return rt

    def getValue(self, className, propKey):
        for s in self.stack:
            if className == s.getClassName():
                v = s.getValue(propKey)
                if v != None:
                    return v
        return None

    def push(self, ms):
        for m in ms:
            self.stack.insert(0, m)
        self.last_pushed = len(ms)

    def pop(self):
        for x in range(self.last_pushed):
            self.stack.pop(0)

class ConverterHandler():

    def __init__(self):
        pass

    def onShapeElement(self, elem, metadatas):
        return elem

    def getViewBox(self, view_box):
        return view_box


class Converter():

    def __init__( self, output=None, input=None, input_string=None, output_file_append=False, indent=2, handler=ConverterHandler()):

        self.handler = handler
        self.reader  = Reader(input=input, input_string=input_string)
        self.printer = Printer(output=output, header='<?xml version="1.0" encoding="utf-8"?>', output_file_append=output_file_append, indent=indent)

    def convert(self):
        obj = self.read();

        self.filtering(obj)

        self.printer.pr(obj)

    def read(self):
        return self.reader.read()


    def filtering(self, root):

        def parseMetadata(metadata_elem):
            attrs      = metadata_elem.getAttribute()
            children   = metadata_elem.getChildren()
            class_name = ([x for x in children if x.getTagName() == "class"][0]).getFirstChild()

            meta = Metadata( metadata_elem.getTagName(), class_name,
                             attrs.get("id"), attrs.get("prototype"))

            for child in children:
                if child.getTagName() == "property":
                    key   = child.getAttribute().get("name")
                    value = child.getFirstChild()
                    meta.setValue(key, value)

            return meta

        def iter (elem, parent, stack):

            if isinstance(elem, Element):
                elem_name = elem.getTagName()
                children  = elem.getChildren()
                meta = [m for m in children if isinstance(m, Element) and m.getTagName() == "metadata"]
                meta = meta[0] if len(meta) > 0 else None

                if meta != None:
                    stack.push(filter(lambda x: not x.prototype_p(),
                                      map(lambda x: parseMetadata(x),
                                          [o for o in meta.getChildren()
                                           if o.getTagName() == "object" or o.getTagName() == "prototype" ])))

                if elem_name in shape_tags:
                    parent.replaceChild(elem, self.handler.onShapeElement(elem, stack))

                elif elem_name == "g" or elem_name == "svg":
                    for child in list(children): # important list(). getting copy list.
                        iter(child, elem, stack)

                if (meta != None):
                    stack.pop()

        iter(root, None, Metadatas())

        svgattr = root.getAttribute()
        svgattr.put("viewBox", " ".join(map(str, apply(self.handler.getViewBox, map(float, svgattr.get("viewBox").split(" "))))))
