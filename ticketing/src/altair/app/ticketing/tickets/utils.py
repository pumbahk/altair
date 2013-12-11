# encoding: utf-8

from lxml import etree
from collections import namedtuple
from collections import Counter
from ..users.models import SexEnum

from altair.svg.constants import SVG_NAMESPACE
from altair.svg.geometry import as_user_unit, translate
from .constants import TS_SVG_EXT_NAMESPACE
from datetime import datetime
import re
import numpy
from ..formatter import Japanese_Japan_Formatter
from .vars_builder import (
    datetime_as_dict, 
    safe_format, 
    TicketCoverDictBuilder, 
    TicketDictBuilder, 
    TicketDictListBuilder
    )

I = numpy.matrix('1 0 0; 0 1 0; 0 0 1', dtype=numpy.float64)

class NumberIssuer(object):
    def __init__(self):
        self.counter = Counter()

    def clear(self):
        self.counter = Counter()

    def __call__(self, k):
        v = self.counter[k] + 1
        self.counter[k] = v
        return v

#b/c
DictBuilder = TicketDictBuilder

_default_builder = DictBuilder(Japanese_Japan_Formatter())
_default_dict_list_builder = TicketDictListBuilder(_default_builder)
build_dict_from_stock = _default_builder.build_dict_from_stock
build_dict_from_venue = _default_builder.build_dict_from_venue
build_dict_from_seat = _default_builder.build_dict_from_seat
build_dict_from_organization = _default_builder.build_dict_from_organization
build_dict_from_event = _default_builder.build_dict_from_event
build_dict_from_performance = _default_builder.build_dict_from_performance
build_dict_from_product = _default_builder.build_dict_from_product
build_dict_from_product_item = _default_builder.build_dict_from_product_item
build_dicts_from_ordered_product_item = _default_dict_list_builder.build_dicts_from_ordered_product_item
build_dicts_from_carted_product_item = _default_dict_list_builder.build_dicts_from_carted_product_item
build_dict_from_ordered_product_item_token = _default_builder.build_dict_from_ordered_product_item_token

_default_cover_builder = TicketCoverDictBuilder(Japanese_Japan_Formatter())
build_cover_dict_from_order = _default_cover_builder.build_dict_from_order

Size = namedtuple('Size', 'width height')
Position = namedtuple('Position', 'x y')
Rectangle = namedtuple('Rectangle', 'x y width height')
Margin = namedtuple('Margin', 'top bottom left right')

class SvgPageSetBuilder(object):
    def __init__(self, page_format, ticket_format):
        orientation = page_format[u'orientation'].lower()
        
        printable_area = Rectangle(
            x=as_user_unit(page_format[u'printable_area'][u'x']),
            y=as_user_unit(page_format[u'printable_area'][u'y']),
            width=as_user_unit(page_format[u'printable_area'][u'width']),
            height=as_user_unit(page_format[u'printable_area'][u'height'])
            )

        if orientation == u'landscape':
            printable_area = Rectangle(
                printable_area.y, printable_area.x,
                printable_area.height, printable_area.width
                )

        ticket_size = Size(
            width=as_user_unit(ticket_format[u'size'][u'width']),
            height=as_user_unit(ticket_format[u'size'][u'height'])
            )

        ticket_margin = Margin(
            top=as_user_unit(page_format[u'ticket_margin'][u'top']),
            bottom=as_user_unit(page_format[u'ticket_margin'][u'bottom']),
            left=as_user_unit(page_format[u'ticket_margin'][u'left']),
            right=as_user_unit(page_format[u'ticket_margin'][u'right'])
            )

        if printable_area.width < ticket_size.width + ticket_margin.left or \
            printable_area.height < ticket_size.height + ticket_margin.top:
            raise ValueError('printable area too small')

        self.page_format = page_format
        self.ticket_format = ticket_format
        self.orientation = orientation
        self.ticket_size = ticket_size
        self.printable_area = printable_area
        self.ticket_margin = ticket_margin
        self.root = self.build_root_element()
        self.pageset = etree.Element(u'{%s}pageSet' % SVG_NAMESPACE)
        self.root.append(self.pageset)
        self.page = None
        self.offset = Position(printable_area.x, printable_area.y)

    @property
    def tickets_per_page(self):
        return (self.printable_area.width + self.ticket_margin.right) // \
            (self.ticket_size.width +
             self.ticket_margin.left +
             self.ticket_margin.right) * \
            (self.printable_area.height + self.ticket_margin.bottom) // \
                (self.ticket_size.height +
                 self.ticket_margin.top +
                 self.ticket_margin.bottom)

    def build_root_element(self):
        width = unicode(as_user_unit(self.page_format[u'size'][u'width']))
        height = unicode(as_user_unit(self.page_format[u'size'][u'height']))

        # Swap width / height if the orientation is 'landscape'
        if self.orientation == u'landscape':
            width, height = height, width
        return etree.Element(
            u'{%s}svg' % SVG_NAMESPACE,
            nsmap={ u'svg': SVG_NAMESPACE, u'ts' : TS_SVG_EXT_NAMESPACE },
            version=u'1.2',
            width=width,
            height=height
            )

    def add(self, svg, queue_id, title=None):
        if self.offset.x + self.ticket_margin.left + self.ticket_size.width > self.printable_area.x + self.printable_area.width:
            self.offset = Position(self.printable_area.x, self.offset.y + self.ticket_size.height + self.ticket_margin.top + self.ticket_margin.bottom)
        if self.offset.y + self.ticket_margin.top + self.ticket_size.height > self.printable_area.y + self.printable_area.height:
            self.offset = Position(self.printable_area.x, self.printable_area.y)
            self.page = None
        if self.page is None:
            self.page = etree.Element(u'{%s}page' % SVG_NAMESPACE)
            if title is not None:
                title_elem = etree.Element(u'{%s}title' % SVG_NAMESPACE)
                title_elem.text = title
                self.page.append(title_elem)
            self.pageset.append(self.page)
        svgroot = svg.getroot() if isinstance(svg, etree._ElementTree) else svg
        svgroot.set(u'x', unicode(self.offset.x + self.ticket_margin.left))
        svgroot.set(u'y', unicode(self.offset.y + self.ticket_margin.top))
        svgroot.set(u'{%s}queue-id' % TS_SVG_EXT_NAMESPACE, unicode(queue_id))
        self.page.append(svgroot)
        self.offset = Position(self.offset.x + self.ticket_size.width + self.ticket_margin.left + self.ticket_margin.right, self.offset.y)

class FallbackSvgPageSetBuilder(object):
    def __init__(self, page_format, ticket_format):
        orientation = page_format[u'orientation'].lower()
        
        printable_area = Rectangle(
            x=as_user_unit(page_format[u'printable_area'][u'x']),
            y=as_user_unit(page_format[u'printable_area'][u'y']),
            width=as_user_unit(page_format[u'printable_area'][u'width']),
            height=as_user_unit(page_format[u'printable_area'][u'height'])
            )

        if orientation == u'landscape':
            printable_area = Rectangle(
                printable_area.y, printable_area.x,
                printable_area.height, printable_area.width
                )

        ticket_size = Size(
            width=as_user_unit(ticket_format[u'size'][u'width']),
            height=as_user_unit(ticket_format[u'size'][u'height'])
            )

        ticket_margin = Margin(
            top=as_user_unit(page_format[u'ticket_margin'][u'top']),
            bottom=as_user_unit(page_format[u'ticket_margin'][u'bottom']),
            left=as_user_unit(page_format[u'ticket_margin'][u'left']),
            right=as_user_unit(page_format[u'ticket_margin'][u'right'])
            )

        self.page_format = page_format
        self.ticket_format = ticket_format
        self.orientation = orientation
        self.ticket_size = ticket_size
        self.printable_area = printable_area
        self.ticket_margin = ticket_margin
        self.root = self.build_root_element()
        self.pageset = etree.Element(u'{%s}pageSet' % SVG_NAMESPACE)
        self.root.append(self.pageset)
        self.offset = Position(printable_area.x, printable_area.y)

    @property
    def tickets_per_page(self):
        return 1

    def build_root_element(self):
        width = unicode(as_user_unit(self.page_format[u'size'][u'width']))
        height = unicode(as_user_unit(self.page_format[u'size'][u'height']))

        # Swap width / height if the orientation is 'landscape'
        if self.orientation == u'landscape':
            width, height = height, width
        return etree.Element(
            u'{%s}svg' % SVG_NAMESPACE,
            nsmap={ u'svg': SVG_NAMESPACE, u'ts' : TS_SVG_EXT_NAMESPACE },
            version=u'1.2',
            width=width,
            height=height
            )

    def add(self, svg, queue_id, title=None):
        page = etree.Element(u'{%s}page' % SVG_NAMESPACE)
        if title is not None:
            title_elem = etree.Element(u'{%s}title' % SVG_NAMESPACE)
            title_elem.text = title
            page.append(title_elem)
        self.pageset.append(page)
        svgroot = svg.getroot() if isinstance(svg, etree._ElementTree) else svg
        svgroot.set(u'x', unicode(self.offset.x + self.ticket_margin.left))
        svgroot.set(u'y', unicode(self.offset.y + self.ticket_margin.top))
        svgroot.set(u'{%s}queue-id' % TS_SVG_EXT_NAMESPACE, unicode(queue_id))
        page.append(svgroot)
        self.offset = Position(self.offset.x + self.ticket_size.width + self.ticket_margin.left + self.ticket_margin.right, self.offset.y)

def transform_matrix_from_ticket_format(ticket_format):
    po = ticket_format.data.get("print_offset")
    if po:
        return translate(-as_user_unit(po.get('x', '0')), -as_user_unit(po.get('y', '0')))
    else:
        return None
