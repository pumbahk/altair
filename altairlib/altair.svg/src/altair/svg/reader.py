# encoding: utf-8

from lxml import html, etree
from lxml.builder import E
from .constants import *
from .geometry import parse_transform, as_user_unit, I
from .path import tokenize_path_data, parse_poly_data, PathDataScanner
import re
import cssutils
import numpy

class VisitorBase(object):
    _dispatch_map = {
        (u'{%s}path' % SVG_NAMESPACE):
            (
                'visit_path',
                [
                    'decorate_styles',
                    'decorate_transform',
                    ]
                ),
        (u'{%s}rect' % SVG_NAMESPACE):
            (
                'visit_rect',
                [
                    'decorate_styles',
                    'decorate_transform',
                    ]
                ),
        (u'{%s}circle' % SVG_NAMESPACE):
            (
                'visit_circle',
                [
                    'decorate_styles',
                    'decorate_transform',
                    ]
                ),
        (u'{%s}ellipse' % SVG_NAMESPACE):
            (
                'visit_ellipse',
                [
                    'decorate_styles',
                    'decorate_transform',
                    ]
                ),
        (u'{%s}polyline' % SVG_NAMESPACE):
            (
                'visit_polyline',
                [
                    'decorate_styles',
                    'decorate_transform',
                    ]
                ),
        (u'{%s}polygon' % SVG_NAMESPACE):
            (
                'visit_polygon',
                [
                    'decorate_styles',
                    'decorate_transform',
                    ]
                ),
        (u'{%s}flowRoot' % SVG_NAMESPACE):
            (
                'visit_flowRoot',
                [
                    'decorate_styles',
                    'decorate_transform',
                    ]
                ),
        (u'{%s}flowRegion' % SVG_NAMESPACE):
            (
                'visit_flowRegion',
                [
                    'decorate_styles',
                    'decorate_transform',
                    ]
                ),
        (u'{%s}flowRect' % SVG_NAMESPACE):
            (
                'visit_flowRect',
                [
                    'decorate_styles',
                    'decorate_transform',
                    ]
                ),
        (u'{%s}text' % SVG_NAMESPACE):
            (
                'visit_text',
                [
                    'decorate_styles',
                    'decorate_transform',
                    ]
                ),
        (u'{%s}g' % SVG_NAMESPACE):
            (
                'visit_g',
                [
                    'decorate_styles',
                    'decorate_transform',
                    ]
                ),
        (u'{%s}svg' % SVG_NAMESPACE):
            (
                'visit_svg',
                [
                    'decorate_styles',
                    ]
                ),
        }

    def decorate_styles(self, fn):
        return fn

    def decorate_transform(self, fn):
        return fn

    def visit_default(self, scanner, elem):
        pass

class Scanner(object):
    def __init__(self, visitor):
        self.visitor = visitor
        dispatch_map = {}
        for tag, (f_name, decorator_names) in visitor._dispatch_map.items():
            fn = getattr(visitor, f_name, visitor.visit_default)
            for decorator_name in decorator_names:
                decorator = getattr(visitor, decorator_name, None)
                if decorator is not None:
                    fn = decorator(fn)
            dispatch_map[tag] = fn
        self.dispatch_map = dispatch_map

    def __call__(self, elems):
        for elem in elems:
            fn = self.dispatch_map.get(elem.tag, self.visitor.visit_default)
            fn(self, elem)
