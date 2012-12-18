import xml.sax
import xml.sax.handler
import xml.sax.saxutils
import sys
import re

# TODO: support other transforms and transform chain
m = re.compile('^translate\((.+),(.+)\)$')

class nullhandler:
    def write(self, arg):
        pass

debug = nullhandler()

class Handler(xml.sax.saxutils.XMLGenerator):
    def __init__(self, out, encoding):
        xml.sax.saxutils.XMLGenerator.__init__(self, out, encoding)
        self.p = (0, 0)
        self.stack = [ ]

    def startElement(self, name, attrs):
        self._out.write("<%s" % name)
        if name == 'g':
            debug.write(" " * len(self.stack))
            debug.write("<g>\n")
            self.stack.append(self.p)
        for k, v in attrs.items():
            if name == 'g':
                if k == 'transform':
                    result = m.match(v)
                    self.p = (self.p[0]+float(result.group(1)),
                              self.p[1]+float(result.group(2)))
                    continue
            elif name == 'rect':
                if k == 'x':
                    v = float(v) + float(self.p[0])
                if k == 'y':
                    v = float(v) + float(self.p[1])
            self._out.write(" %s=\"%s\"" % (k, v))
        self._out.write(">")

    def endElement(self, name):
        self._out.write("</%s>" % name)
        if name == 'g':
            self.p = self.stack.pop()
            debug.write(" " * len(self.stack))
            debug.write("</g>\n")

if __name__=="__main__":
#   debug = sys.stderr 
    parser = xml.sax.make_parser()
    parser.setContentHandler(Handler(sys.stdout, 'utf-8'))
    parser.setFeature(xml.sax.handler.feature_namespaces, False)
    parser.parse(sys.stdin)
