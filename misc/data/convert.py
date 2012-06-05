#!/usr/bin/env python -S
# -*- coding: utf-8 -*-
from converter import Converter, Element, Attributes, Metadata, Metadatas
import os
import sys
import io

# convert function
def convert(elem, metadatas):
    attr = elem.getAttribute();
    return not attr.get("class") == "seat"

def main():
    argvs = sys.argv
    argc  = len(argvs)
    src   = None
    tgt   = None

    if (argc < 2):
        print 'Usage: $ python %s sourcefile.xml targetfile.tiny.xml' % argvs[0]
        quit(1)

    if (argc < 3):
        src = argvs[1]
        fn, fx = os.path.splitext(src)
        tgt = fn + '.tiny.xml'

    else:
        src = argvs[1]
        tgt = argvs[2]

    print 'SOURCE:%s TARGET:%s' % (src, tgt)
    print 'defaultencoding:%s' % sys.getdefaultencoding()

    converter = Converter(input=src, output=tgt, indent=1, fn=convert)
    converter.convert()

main()
