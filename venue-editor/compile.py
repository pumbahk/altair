#!/usr/bin/python -S
import sys
import os
import re
import argparse
import random
from cStringIO import StringIO

class ApplicationException(Exception):
    pass

def gencharset(spec):
    retval = ''
    for item in re.finditer(r'([^\\-]|\\-|\\\\)(?:-([^\\-]|\\-|\\\\))?', spec):
        if item.group(2):
            retval += ''.join(chr(c) for c in range(ord(item.group(1)), ord(item.group(2)) + 1))
        else:
            retval += item.group(1)
    return retval

class IDGenerator(object):
    INITIAL_CHARS = gencharset("A-Za-z_")
    SUCCEEDING_CHARS = gencharset("0-9A-Za-Z_")

    def __init__(self):
        self.generated = set()

    def __call__(self):
        retval = random.choice(self.__class__.INITIAL_CHARS)
        for i in range(0, 15):
            retval += random.choice(self.__class__.SUCCEEDING_CHARS)
        return retval

class Processor(object):
    def __init__(self):
        self.included_files = set()
        self.search_path = set(['.'])
        self.libs = {}
        self.out = StringIO()
        self.idgen = IDGenerator()
        self.externs = set()

    def lookup_file(self, file, includer=None):
        for dir in self.search_path:
            if os.path.isabs(dir):
                path = os.path.join(dir, file)
            else:
                if includer is None:
                    raise ApplicationException("Relative path specified but no includer given")
                path = os.path.join(os.path.dirname(includer), dir, file)
            if os.path.exists(path):
                return os.path.normpath(path)
        return None

    def compose_source(self, file, out):
        self.included_files.add(file)
        mydeps = list()
        with open(file, 'r') as f:
            out.write('\n\n/************** %s **************/\n' % os.path.basename(file))
            for line in f:
                includes = re.findall(r'include\s*\(\"(.+?)\"\)', line)
                if includes:
                    for included_file_name in includes:
                        included = self.lookup_file(included_file_name, file)
                        if included in self.included_files:
                            continue
                        if included is None:
                            raise ApplicationException("File not found: %s" % included_file_name)
                        self.compose_source(included, out)

                else:
                    def repl(match):
                        required_file_name = match.group(2)
                        required = self.lookup_file(required_file_name, file)
                        if required is None:
                            raise ApplicationException("File not found: %s" % required_file_name)
                        pair = self.libs.get(required)
                        if pair is None:
                            id = self.idgen()
                            self.libs[required] = (id, None, None)
                            out = StringIO()
                            deps = self.compose_source(required, out)
                            pair = self.libs[required] = (id, out.getvalue(), deps)
                        mydeps.append(required)
                        return "__LIBS__['%s']" % pair[0]

                    line = re.sub(r'''require\s*\((["'])(.+)(\1)\)''', repl, line)
                    out.write(line)

        return mydeps

    def read(self, file):
        for line in open(file, 'r'):
            g = re.match(r'''/\*\s*extern\s*\*/\s*var\s+([^;]+)''', line)
            if g is not None:
                self.externs.update(re.split('\s*,\s*', g.group(1)))
        self.compose_source(file, self.out)

    def write(self, out):
        # TODO: dependency resolution
        out.write("(function (%s) {\n" % ', '.join(self.externs))
        out.write("var __LIBS__ = {};\n")
        has_written = set()

        def write_lib(path, pair):
            if path not in has_written:
                has_written.add(path)
                deps = pair[2]
                for i in deps:
                    write_lib(i, self.libs[i])
                out.write("__LIBS__['%s'] = (function (exports) { (function () { %s })(); return exports; })({});\n" % (pair[0], pair[1]))

        for path, pair in self.libs.iteritems():
            write_lib(path, pair)

        out.write(self.out.getvalue())
        out.write("})(%s);\n" % ', '.join('window.%s' % extern for extern in self.externs))

def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-o', type=str)
    argparser.add_argument('file', nargs='+', type=str)
    options = argparser.parse_args()
    if options.o is not None:
        out = open(options.o, 'w')
    else:
        out = sys.stdout
    try:
        p = Processor()
        for file in options.file:
            p.read(os.path.abspath(file))
        p.write(out)
    except:
        if options.o is not None:
            out.close()
            os.unlink(options.o)
        raise

if __name__ == '__main__':
    try:
        main()
    except ApplicationException as e:
        print >>sys.stderr, e.message
