# -*- coding:utf-8 -*-
"""
template with inheritance
"""
def main(app):
    from pyramid.renderers import render
    import codecs
    import sys
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout)
    print render("altaircms:templates/front/original3/instance.mako", {})

