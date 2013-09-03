# encoding: utf-8

from lxml import etree
from collections import namedtuple

from ..users.models import SexEnum

from .constants import SVG_NAMESPACE, TS_SVG_EXT_NAMESPACE
import re
import numpy
from ..formatter import Japanese_Japan_Formatter
from .vars_builder import (
    datetime_as_dict, 
    safe_format, 
    TicketCoverDictBuilder, 
    TicketDictBuilder
    )
I = numpy.matrix('1 0 0; 0 1 0; 0 0 1', dtype=numpy.float64)


#b/c
DictBuilder = TicketDictBuilder

_default_builder = DictBuilder(Japanese_Japan_Formatter())
build_dict_from_stock = _default_builder.build_dict_from_stock
build_dict_from_venue = _default_builder.build_dict_from_venue
build_dict_from_seat = _default_builder.build_dict_from_seat
build_dict_from_organization = _default_builder.build_dict_from_organization
build_dict_from_event = _default_builder.build_dict_from_event
build_dict_from_performance = _default_builder.build_dict_from_performance
build_dict_from_product = _default_builder.build_dict_from_product
build_dict_from_product_item = _default_builder.build_dict_from_product_item
build_dicts_from_ordered_product_item = _default_builder.build_dicts_from_ordered_product_item
build_dicts_from_carted_product_item = _default_builder.build_dicts_from_carted_product_item
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


def as_user_unit(size, rel_unit=None):
    if size is None:
        return None
    spec = re.match('(-?[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(pt|pc|mm|cm|in|px|em|%)?', size.strip().lower())
    if spec is None:
        raise Exception('Invalid length / size specifier: ' + size)
    degree = float(spec.group(1))
    unit = spec.group(2) or 'px'
    if unit == 'pt':
        return degree * 1.25
    elif unit == 'pc':
        return degree * 15
    elif unit == 'mm':
        return degree * 90 / 25.4
    elif unit == 'cm':
        return degree * 90 / 2.54
    elif unit == 'in':
        return degree * 90.
    elif unit == 'px':
        return degree
    elif unit == 'em':
        if rel_unit is None:
            raise Exception('Relative size specified where no unit size is given in the applied context')
        return rel_unit * degree
    elif unit == '%':
        if rel_unit is None:
            raise Exception('Relative size specified where no unit size is given in the applied context')
        return rel_unit * degree / 100.

def translate(x, y):
    return numpy.matrix(
        [
            [1., 0., float(x)],
            [0., 1., float(y)],
            [0., 0., 1.]
            ],
        dtype=numpy.float64)

def parse_transform(transform_str):
    for g in re.finditer(ur'\s*([A-Za-z_-][0-9A-Za-z_-]*)\s*\(\s*((?:[^\s,]+(?:\s*,\s*|\s+))*[^\s,]+)\s*\)\s*', transform_str):
        f = g.group(1)
        args = re.split(ur'\s*,\s*|\s+',g.group(2).strip())
        if f == u'matrix':
            if len(args) != 6:
                raise Exception('invalid number of arguments for matrix()')
            return numpy.matrix(
                [
                    [float(args[0]), float(args[2]), float(args[4])],
                    [float(args[1]), float(args[3]), float(args[5])],
                    [0., 0., 1.]
                    ],
                dtype=numpy.float64)
        elif f == u'translate':
            if len(args) != 2:
                raise Exception('invalid number of arguments for translate()')
            return translate(args[0], args[1])
        elif f == u'scale':
            if len(args) != 2:
                raise Exception('invalid number of arguments for scale()')
            return numpy.matrix(
                [
                    [float(args[0]), 0., 0.],
                    [0., float(args[1]), 0.],
                    [0., 0., 1.]
                    ],
                dtype=numpy.float64)
        elif f == u'rotate':
            if len(args) != 1:
                raise Exception('invalid number of arguments for rotate()')
            t = float(args[0]) * numpy.pi / 180.
            c = numpy.sin(t)
            s = numpy.sin(t)
            return numpy.matrix(
                [
                    [c, -s, 0.],
                    [s, c, 0.],
                    [0., 0., 1.]
                    ],
                dtype=numpy.float64)
        elif f == u'skeyX':
            if len(args) != 1:
                raise Exception('invalid number of arguments for skewX()')
            t = float(args[0]) * numpy.pi / 180.
            ta = numpy.tan(t)
            return numpy.matrix(
                [
                    [1., ta, 0.],
                    [0., 1., 0.],
                    [0., 0., 1.]
                    ],
                dtype=numpy.float64)
        elif f == u'skeyY':
            if len(args) != 1:
                raise Exception('invalid number of arguments for skewY()')
            t = float(args[0]) * numpy.pi / 180.
            ta = numpy.tan(t)
            return numpy.matrix(
                [
                    [1., 0., 0.],
                    [ta, 1., 0.],
                    [0., 0., 1.]
                    ],
                dtype=numpy.float64)

class PathDataScanner(object):
    def __init__(self, iter, handler):
        self.iter = iter
        self.handler = handler
        self.current_position = (0, 0)
        self.last_qb_control_point = None
        self.last_cb_control_point = None
        self.next_op = None

    def scan_z(self, operand):
        if len(operand) > 0:
            raise Exception('closepath does not take any arguments')
        self.handler.close_path()
        self.last_qb_control_point = None
        self.last_cb_control_point = None

    scan_Z = scan_z

    def scan_h(self, operand):
        if len(operand) == 0:
            raise Exception('horizontalline takes at least 1 argument')
        for oper in operand:
            x = self.current_position[0] + float(oper)
            self.handler.line_to(x, self.current_position[1])
            self.current_position = (x, self.current_position[1])
        self.last_qb_control_point = None
        self.last_cb_control_point = None

    def scan_H(self, operand):
        if operand == 0:
            raise Exception('horizontalline takes at least 1 argument')
        for oper in operand:
            x = float(oper)
            self.handler.line_to(x, self.current_position[1])
            self.current_position = (x, self.current_position[1])
        self.last_qb_control_point = None
        self.last_cb_control_point = None

    def scan_v(self, operand):
        if len(operand) == 0:
            raise Exception('verticalline takes at least 1 argument')
        for oper in operand:
            y = self.current_position[1] + float(oper)
            self.handler.line_to(self.current_position[0], y)
            self.current_position = (self.current_position[0], y)
        self.last_qb_control_point = None
        self.last_cb_control_point = None

    def scan_V(self, operand):
        if len(operand) == 0:
            raise Exception('verticalline takes at least 1 argument')
        for oper in operand:
            y = float(oper)
            self.handler.line_to(self.current_position[0], y)
            self.current_position = (self.current_position[0], y)
        self.last_qb_control_point = None
        self.last_cb_control_point = None

    def scan_m(self, operand):
        if operand == 0 or len(operand) % 2 != 0:
            raise Exception('moveto takes 2 * n arguments')
        i = iter(operand)
        try:
            x = self.current_position[0] + float(i.next())
            y = self.current_position[1] + float(i.next())
            self.handler.move_to(x, y)
            self.current_position = (x, y)
            while True:
                x = self.current_position[0] + float(i.next())
                y = self.current_position[1] + float(i.next())
                self.handler.line_to(x, y)
                self.current_position = (x, y)
        except StopIteration:
            pass
        self.last_qb_control_point = None
        self.last_cb_control_point = None

    def scan_M(self, operand):
        if operand == 0 or len(operand) % 2 != 0:
            raise Exception('moveto takes 2 * n arguments')
        i = iter(operand)
        try:
            x = float(i.next())
            y = float(i.next())
            self.handler.move_to(x, y)
            self.current_position = (x, y)
            while True:
                x = float(i.next())
                y = float(i.next())
                self.handler.line_to(x, y)
                self.current_position = (x, y)
        except StopIteration:
            pass
        self.last_qb_control_point = None
        self.last_cb_control_point = None

    def scan_l(self, operand):
        if operand == 0 or len(operand) % 2 != 0:
            raise Exception('lineto takes 2 * n arguments')
        i = iter(operand)
        try:
            while True:
                x = self.current_position[0] + float(i.next())
                y = self.current_position[1] + float(i.next())
                self.handler.line_to(x, y)
                self.current_position = (x, y)
        except StopIteration:
            pass
        self.last_qb_control_point = None
        self.last_cb_control_point = None

    def scan_L(self, operand):
        if operand == 0 or len(operand) % 2 != 0:
            raise Exception('lineto takes 2 * n arguments')
        i = iter(operand)
        try:
            while True:
                x = float(i.next())
                y = float(i.next())
                self.handler.line_to(x, y)
                self.current_position = (x, y)
        except StopIteration:
            pass
        self.last_qb_control_point = None
        self.last_cb_control_point = None

    def scan_t(self, operand):
        if operand == 0 or len(operand) % 2 != 0:
            raise Exception('curvetosmooth takes 2 * n arguments')
        i = iter(operand)
        try:
            while True:
                x = self.current_position[0] + float(i.next())
                y = self.current_position[1] + float(i.next())
                if self.last_qb_control_point is None:
                    x1 = self.current_position[0]
                    y1 = self.current_position[1]
                else:
                    x1 = self.current_position[0] + (self.current_position[0] - self.last_qb_control_point[0])
                    y1 = self.current_position[1] + (self.current_position[1] - self.last_qb_control_point[1])
                self.handler.curve_to_qb(x1, y1, x, y)
                self.current_position = (x, y)
                self.last_qb_control_point = (x1, y1)
        except StopIteration:
            pass
        self.last_cb_control_point = None

    def scan_T(self, operand):
        if operand == 0 or len(operand) % 2 != 0:
            raise Exception('curvetosmooth takes 2 * n arguments')
        i = iter(operand)
        try:
            while True:
                x = float(i.next())
                y = float(i.next())
                if self.last_qb_control_point is None:
                    x1 = self.current_position[0]
                    y1 = self.current_position[1]
                else:
                    x1 = self.current_position[0] + (self.current_position[0] - self.last_qb_control_point[0])
                    y1 = self.current_position[1] + (self.current_position[1] - self.last_qb_control_point[1])
                self.handler.curve_to_qb(x1, y1, x, y)
                self.current_position = (x, y)
                self.last_qb_control_point = (x1, y1)
        except StopIteration:
            pass
        self.last_cb_control_point = None

    def scan_s(self, operand):
        if operand == 0 or len(operand) % 4 != 0:
            raise Exception('curvetosmooth takes 4 * n arguments')
        i = iter(operand)
        try:
            while True:
                if self.last_cb_control_point is None:
                    x1 = self.current_position[0]
                    y1 = self.current_position[1]
                else:
                    x1 = self.current_position[0] + (self.current_position[0] - self.last_cb_control_point[0])
                    y1 = self.current_position[1] + (self.current_position[1] - self.last_cb_control_point[1])
                x2 = self.current_position[0] + float(i.next())
                y2 = self.current_position[1] + float(i.next())
                x = self.current_position[0] + float(i.next())
                y = self.current_position[1] + float(i.next())
                self.handler.curve_to(x1, y1, x2, y2, x, y)
                self.current_position = (x, y)
                self.last_cb_control_point = (x2, y2)
        except StopIteration:
            pass
        self.last_qb_control_point = None

    def scan_S(self, operand):
        if operand == 0 or len(operand) % 4 != 0:
            raise Exception('curvetosmooth takes 4 * n arguments')
        i = iter(operand)
        try:
            while True:
                if self.last_cb_control_point is None:
                    x1 = self.current_position[0]
                    y1 = self.current_position[1]
                else:
                    x1 = self.current_position[0] + (self.current_position[0] - self.last_cb_control_point[0])
                    y1 = self.current_position[1] + (self.current_position[1] - self.last_cb_control_point[1])
                x2 = float(i.next())
                y2 = float(i.next())
                x = float(i.next())
                y = float(i.next())
                self.handler.curve_to(x1, y1, x2, y2, x, y)
                self.current_position = (x, y)
                self.last_cb_control_point = (x2, y2)
        except StopIteration:
            pass
        self.last_qb_control_point = None

    def scan_q(self, operand):
        if operand == 0 or len(operand) % 4 != 0:
            raise Exception('curvetoqb takes 4 * n arguments')
        i = iter(operand)
        try:
            while True:
                x1 = self.current_position[0] + float(i.next())
                y1 = self.current_position[1] + float(i.next())
                x = self.current_position[0] + float(i.next())
                y = self.current_position[1] + float(i.next())
                self.last_qb_control_point = (x1, y1)
                self.handler.curve_to_qb(x1, y1, x, y)
                self.current_position = (x, y)
        except StopIteration:
            pass
        self.last_cb_control_point = None

    def scan_Q(self, operand):
        if operand == 0 or len(operand) % 4 != 0:
            raise Exception('curvetoqb takes 4 * n arguments')
        i = iter(operand)
        try:
            while True:
                x1 = float(i.next())
                y1 = float(i.next())
                x = float(i.next())
                y = float(i.next())
                self.last_qb_control_point = (x1, y1)
                self.handler.curve_to_qb(x1, y1, x, y)
                self.current_position = (x, y)
        except StopIteration:
            pass
        self.last_cb_control_point = None

    def scan_c(self, operand):
        if operand == 0 or len(operand) % 6 != 0:
            raise Exception('curveto takes 6 * n arguments')
        i = iter(operand)
        try:
            while True:
                x1 = self.current_position[0] + float(i.next())
                y1 = self.current_position[1] + float(i.next())
                x2 = self.current_position[0] + float(i.next())
                y2 = self.current_position[1] + float(i.next())
                x = self.current_position[0] + float(i.next())
                y = self.current_position[1] + float(i.next())
                self.handler.curve_to(x1, y1, x2, y2, x, y)
                self.current_position = (x, y)
                self.last_cb_control_point = (x2, y2)
        except StopIteration:
            pass
        self.last_qb_control_point = None

    def scan_C(self, operand):
        if operand == 0 or len(operand) % 6 != 0:
            raise Exception('curveto takes 6 * n arguments')
        i = iter(operand)
        try:
            while True:
                x1 = float(i.next())
                y1 = float(i.next())
                x2 = float(i.next())
                y2 = float(i.next())
                x = float(i.next())
                y = float(i.next())
                self.handler.curve_to(x1, y1, x2, y2, x, y)
                self.current_position = (x, y)
                self.last_cb_control_point = (x2, y2)
        except StopIteration:
            pass
        self.last_qb_control_point = None

    def scan_a(self, operand):
        if operand == 0 or len(operand) % 7 != 0:
            raise Exception('arc takes 7 * n arguments')
        i = iter(operand)
        try:
            while True:
                rx = float(i.next())
                ry = float(i.next())
                phi = float(i.next())
                largearc = bool(i.next())
                sweep = bool(i.next())
                x = self.current_position[0] + float(i.next())
                y = self.current_position[1] + float(i.next())
                self.handler.arc(rx, ry, phi, largearc, sweep, x, y)
                self.current_position = (x, y)
        except StopIteration:
            pass
        self.last_cb_control_point = None
        self.last_qb_control_point = None

    def scan_A(self, operand):
        if operand == 0 or len(operand) % 7 != 0:
            raise Exception('arc takes 7 * n arguments')
        i = iter(operand)
        try:
            while True:
                rx = float(i.next())
                ry = float(i.next())
                phi = float(i.next())
                largearc = bool(i.next())
                sweep = bool(i.next())
                x = float(i.next())
                y = float(i.next())
                self.handler.arc(rx, ry, phi, largearc, sweep, x, y)
                self.current_position = (x, y)
        except StopIteration:
            pass
        self.last_cb_control_point = None
        self.last_qb_control_point = None

    def __call__(self):
        fn = None
        operand = []
        for op in self.iter:
            next_fn = getattr(self, 'scan_' + op, None)
            if fn is not None:
                if next_fn is not None:
                    fn(operand)
                    fn = next_fn
                    operand = []
                else:
                    operand.append(op)
            else:
                fn = next_fn
        if fn is not None:
            fn(operand)

NUM_REGEX = ur'(-?(?:(?:[0-9]+(?:\.[0-9]+)?|\.[0-9]+)(?:[eE][-+]?[0-9]+)?))'

def tokenize_path_data(path):
    return (g.group(0) for g in re.finditer(NUM_REGEX + ur'|[A-Za-z_]+', path))

def parse_poly_data(poly):
    return ((float(g.group(1)), float(g.group(2))) for g in re.finditer(NUM_REGEX + ur'(?:\s+(?:,\s*)?|,\s*)' + NUM_REGEX, poly))

def transform_matrix_from_ticket_format(ticket_format):
    po = ticket_format.data.get("print_offset")
    if po:
        return translate(-as_user_unit(po.get('x', '0')), -as_user_unit(po.get('y', '0')))
    else:
        return None
