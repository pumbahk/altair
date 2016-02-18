# encoding: utf-8

from lxml import html, etree
from lxml.builder import E
from altair.svg.constants import *
from altair.app.ticketing.tickets.constants import *
from altair.svg.reader import Scanner, VisitorBase
from altair.svg.geometry import parse_transform, as_user_unit, I
from altair.svg.path import tokenize_path_data, parse_poly_data, PathDataScanner
import re
import cssutils
import numpy
import logging
import itertools
from collections import OrderedDict

__all__ = (
    'to_opcodes',
    'convert_svg',
    )

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SEJ_ECLEVEL_MAP = {
    'h': 'H',
    'l': 'Q',
    'm': 'Q',
    'q': 'Q',
    }

QR_LEVEL_TABLE_BINARY = [
    [ 11,  20,  32,  46,  60,  74,  86,  108, 130, 151, 177 ],
    [  7,  14,  24,  34,  44,  58,  64,   84,  98, 119, 137 ]
    ]

QR_LEVEL_TABLE_KANJI = [
    [  7,  12,  20,  28,  37,  45,  53,  66,  80,  93, 109 ],
    [  4,   8,  15,  21,  27,  36,  39,  52,  60,  74,  85 ]
    ]

QR_LEVEL_TABLE_ALNUM = [
    [ 16, 29, 47, 67, 87, 108, 125, 157, 189, 221, 259 ],
    [ 10, 20, 35, 50, 64,  84,  93, 122, 143, 174, 200 ]
    ]

QR_LEVEL_TABLE_NUM = [
    [ 27,  48,  77, 111, 144, 178, 207, 259, 312, 364, 427 ],
    [ 17,  34,  58,  82, 106, 139, 154, 202, 235, 288, 331 ]
    ]

QR_LEVEL_TABLES = [
    QR_LEVEL_TABLE_NUM,
    QR_LEVEL_TABLE_ALNUM,
    QR_LEVEL_TABLE_KANJI,
    QR_LEVEL_TABLE_BINARY
    ]

def _len(value):
    try:
        return len(value)
    except TypeError:
        return None

def singletons(elem):
    def helper(l, elem):
        l.append(elem)
        tail, text = elem.tail, elem.text
        if len(elem) == 0:
            return True
        elif len(elem) == 1 and not (tail and tail.strip()) and not (text and text.strip()):
            return helper(l, elem[0])
        else:
            return False
    retval = []
    if helper(retval, elem):
        return retval
    else:
        return None

class TicketNotationEmitter(object):
    def __init__(self, result, notation_version):
        self.result = result
        self.notation_version = notation_version

    def emit_scalar_value(self, value, string_as_symbol=False):
        if isinstance(value, basestring):
            if string_as_symbol and not re.match('[\s"]', value):
                self.result.append(u':' + value)
            else:
                self.result.append(u'"' + unicode(value).replace('\\', '\\\\').replace('"', '\\"') + u'"')
        elif isinstance(value, bool):
            self.result.append(u'1' if value else u'0')
        elif isinstance(value, (int, long)):
            self.result.append(unicode(value))
        elif isinstance(value, float):
            if value.is_integer():
                self.result.append(unicode(int(value)))
            else:
                self.result.append(unicode(value))
        else:
            raise TypeError(value)

    def emit_symbol(self, value):
        value = unicode(value)
        if re.match('[\s"]', value):
            raise ValueError('A symbol cannot contain any space or \'"\'')
        self.result.append(u':' + value)

    def emit_scale(self, value):
        self.emit_scalar_value(float(value))
        self.result.append(u'S')

    def emit_font_size(self, value):
        self.emit_scalar_value(float(value))
        self.result.append(u'fs')

    def emit_line_height(self, value):
        self.emit_scalar_value(float(value))
        self.result.append(u'lh')

    def emit_push_class(self, value):
        self.emit_symbol(value)
        self.result.append(u'hc')

    def emit_pop_class(self):
        self.result.append(u'pc')

    def emit_set_class(self, value):
        self.emit_symbol(value)
        self.result.append(u'sc')

    def emit_fill_color(self, value):
        self.emit_scalar_value(value, True)
        self.result.append(u'rg')

    def emit_stroke_color(self, value):
        self.emit_scalar_value(value, True)
        self.result.append(u'RG')

    def emit_stroke_width(self, value):
        self.emit_scalar_value(value)
        self.result.append(u'Sw')

    def emit_unit(self, value):
        self.emit_symbol(value)
        self.result.append(u'U')

    def emit_show_text(self, anchor, text):
        if self.notation_version >= 2:
            self.emit_symbol(unicode(anchor))
            self.emit_scalar_value(unicode(text))
            self.result.append(u'x')

    def emit_show_dom_node_text(self, anchor, path):
        if self.notation_version >= 2:
            self.emit_symbol(unicode(anchor))
            self.emit_scalar_value(unicode(path))
            self.result.append(u'xn')
            self.result.append(u'sxn')
            self.result.append(u'x')

    def emit_show_text_block(self, width, height, text):
        self.emit_scalar_value(float(width))
        self.emit_scalar_value(float(height))
        self.emit_scalar_value(unicode(text))
        self.result.append(u'X')

    def emit_show_dom_node_text_block(self, width, height, path):
        self.emit_scalar_value(float(width))
        self.emit_scalar_value(float(height))
        self.emit_scalar_value(unicode(path))
        self.result.append(u'xn')
        self.result.append(u'sxn')
        self.result.append(u'X')

    def emit_transform(self, a, b, c, d, e, f):
        self.emit_scalar_value(float(a))
        self.emit_scalar_value(float(b))
        self.emit_scalar_value(float(c))
        self.emit_scalar_value(float(d))
        self.emit_scalar_value(float(e))
        self.emit_scalar_value(float(f))
        self.result.append(u'cm')

    def emit_new_path(self):
        self.result.append(u'N')

    def emit_move_to(self, x, y):
        self.emit_scalar_value(float(x))
        self.emit_scalar_value(float(y))
        self.result.append(u'm')

    def emit_line_to(self, x, y):
        self.emit_scalar_value(float(x))
        self.emit_scalar_value(float(y))
        self.result.append(u'l')

    def emit_curve_to(self, x1, y1, x2, y2, x3, y3):
        self.emit_scalar_value(float(x1))
        self.emit_scalar_value(float(y1))
        self.emit_scalar_value(float(x2))
        self.emit_scalar_value(float(y2))
        self.emit_scalar_value(float(x3))
        self.emit_scalar_value(float(y3))
        self.result.append(u'c')

    def emit_curve_to_s1(self, x2, y2, x3, y3):
        self.emit_scalar_value(float(x2))
        self.emit_scalar_value(float(y2))
        self.emit_scalar_value(float(x3))
        self.emit_scalar_value(float(y3))
        self.result.append(u'v')

    def emit_curve_to_s2(self, x1, y1, x3, y3):
        self.emit_scalar_value(float(x1))
        self.emit_scalar_value(float(y1))
        self.emit_scalar_value(float(x3))
        self.emit_scalar_value(float(y3))
        self.result.append(u'y')

    def emit_quadratic_curve_to(self, x1, y1, x2, y2):
        self.emit_scalar_value(float(x1))
        self.emit_scalar_value(float(y1))
        self.emit_scalar_value(float(x2))
        self.emit_scalar_value(float(y2))
        self.result.append(u'q')

    def emit_arc(self, rx, ry, phi, largeArc, sweep, x, y):
        self.emit_scalar_value(float(rx)) 
        self.emit_scalar_value(float(ry)) 
        self.emit_scalar_value(float(phi)) 
        self.emit_scalar_value(bool(largeArc))
        self.emit_scalar_value(bool(sweep))
        self.emit_scalar_value(float(x)) 
        self.emit_scalar_value(float(y)) 
        self.result.append(u'a')

    def emit_close_path(self):
        self.result.append(u'h')

    def emit_fill(self):
        self.result.append('f')

    def emit_stroke(self):
        self.result.append('s')

    def emit_stroke_and_fill(self):
        self.result.append('B')

class Assembler(object):
    def __init__(self, result):
        self.result = result

    def emit_scale(self, value):
        self.result.append(('scale', [value]))

    def emit_font_size(self, value):
        self.result.append(('font_size', [value]))

    def emit_line_height(self, value):
        self.result.append(('line_height', [value]))

    def emit_push_class(self, value):
        self.result.append(('push_class', [value]))

    def emit_pop_class(self):
        self.result.append(('pop_class', []))

    def emit_set_class(self, value):
        self.result.append(('set_class', [value]))

    def emit_fill_color(self, value):
        self.result.append(('fill_color', [value]))

    def emit_stroke_color(self, value):
        self.result.append(('stroke_color', [value]))

    def emit_stroke_width(self, value):
        self.result.append(('stroke_width', [value]))

    def emit_unit(self, value):
        self.result.append(('unit', [value]))

    def emit_show_text(self, anchor, text):
        self.result.append(('show_text', [anchor, text]))

    def emit_show_dom_node_text(self, anchor, path):
        self.result.append(('show_dom_node_text', [anchor, path]))

    def emit_show_text_block(self, width, height, text):
        self.result.append(('show_text_block', [width, height, text]))

    def emit_show_dom_node_text_block(self, width, height, path):
        self.result.append(('show_dom_node_text_block', [width, height, path]))

    def emit_transform(self, a, b, c, d, e, f):
        self.result.append(('transform', [a, b, c, d, e, f]))

    def emit_new_path(self):
        self.result.append(('new_path', []))

    def emit_move_to(self, x, y):
        self.result.append(('move_to', [x, y]))

    def emit_line_to(self, x, y):
        self.result.append(('line_to', [x, y]))

    def emit_curve_to(self, x1, y1, x2, y2, x3, y3):
        self.result.append(('curve_to', [x1, y1, x2, y2, x3, y3]))

    def emit_curve_to_s1(self, x2, y2, x3, y3):
        self.result.append(('curve_to_s1', [x2, y2, x3, y3]))

    def emit_curve_to_s2(self, x1, y1, x3, y3):
        self.result.append(('curve_to_s2', [x1, y1, x3, y3]))

    def emit_quadratic_curve_to(self, x1, y1, x2, y2):
        self.result.append(('quadratic_curve_to', [x1, y1, x2, y2]))

    def emit_arc(self, rx, ry, phi, largeArc, sweep, x, y):
        self.result.append(('arc', [rx, ry, phi, largeArc, sweep, x, y]))

    def emit_close_path(self):
        self.result.append(('close_path', []))

    def emit_fill(self):
        self.result.append(('fill', []))

    def emit_stroke(self):
        self.result.append(('stroke', []))

    def emit_stroke_and_fill(self):
        self.result.append(('stroke_and_fill', []))

class Optimizer(object):
    def __init__(self):
        pass

    def remove_unnecessary_modifiers(self, opcodes):
        for i in reversed(range(0, len(opcodes))):
            op, _ = opcodes[i]
            if op in ('fill', 'stroke', 'stroke_and_fill', 'show_text', 'show_text_block', 'show_dom_node_text', 'show_dom_node_text_block'):
                break
        return opcodes[0:i+1]

    def remove_unnecessary_specifiers(self, opcodes):
        nonstacked_style_specifiers = ('fill_color', 'stroke_color', 'stroke_width', 'font_size', 'line_height')
        retval = []
        accumulated_styles = None
        state = 0
        for pair in opcodes:
            if state == 0:
                if pair[0] in nonstacked_style_specifiers:
                    accumulated_styles = OrderedDict()
                    accumulated_styles[pair[0]] = pair
                    state = 1
                else:
                    retval.append(pair)
            elif state == 1:
                if pair[0] in nonstacked_style_specifiers:
                    accumulated_styles[pair[0]] = pair
                else:
                    retval.extend(accumulated_styles.values())
                    retval.append(pair)
                    pair = 0
                    state = 0
        return retval

    def remove_unnecessary_push_pop(self, opcodes):
        retval = []
        last_push = None
        for pair in opcodes:
            if pair[0] == 'push_class':
                if last_push:
                    retval.append(last_push)
                last_push = pair
            elif pair[0] == 'pop_class':
                if not last_push:
                    retval.append(pair)
                else:
                    last_push = None
            else:
                if last_push:
                    retval.append(last_push)
                    last_push = None
                retval.append(pair)
        if last_push:
            retval.append(last_push)
        return retval

    def __call__(self, opcodes):
        opcodes = self.remove_unnecessary_push_pop(opcodes)
        opcodes = self.remove_unnecessary_specifiers(opcodes)
        opcodes = self.remove_unnecessary_modifiers(opcodes)
        return opcodes

def emit_opcodes(emitter, opcodes):
    for op, args in opcodes:
        getattr(emitter, 'emit_' + op)(*args)

class ScaleFilter(object):
    def __init__(self, outer, base_scale):
        self.outer = outer
        self.outer.emit_scale(base_scale)
        self.base_scale = base_scale

    def emit_scale(self, value):
        self.outer.emit_scale(int(float(value) / self.base_scale))

    def emit_font_size(self, value):
        self.outer.emit_font_size(value)

    def emit_line_height(self, value):
        self.outer.emit_line_height(value)

    def emit_push_class(self, value):
        self.outer.emit_push_class(value)

    def emit_pop_class(self):
        self.outer.emit_pop_class()

    def emit_set_class(self, value):
        self.outer.emit_set_class(value)

    def emit_fill_color(self, value):
        self.outer.emit_fill_color(value)

    def emit_stroke_color(self, value):
        self.outer.emit_stroke_color(value)

    def emit_stroke_width(self, value):
        self.outer.emit_stroke_width(int(float(value) / self.base_scale))

    def emit_unit(self, value):
        self.outer.emit_unit(value)

    def emit_show_text(self, anchor, text):
        self.outer.emit_show_text(anchor, text)

    def emit_show_dom_node_text(self, anchor, path):
        self.outer.emit_show_dom_node_text(anchor, path)

    def emit_show_text_block(self, width, height, text):
        self.outer.emit_show_text_block(
            int(float(width) / self.base_scale),
            int(float(height) / self.base_scale),
            text)

    def emit_show_dom_node_text_block(self, width, height, path):
        self.outer.emit_show_dom_node_text_block(
            int(float(width) / self.base_scale),
            int(float(height) / self.base_scale),
            path)

    def emit_transform(self, a, b, c, d, e, f):
        self.outer.emit_transform(a, b, c, d, e, f)

    def emit_new_path(self):
        self.outer.emit_new_path()

    def emit_move_to(self, x, y):
        self.outer.emit_move_to(
            int(float(x) / self.base_scale),
            int(float(y) / self.base_scale))

    def emit_line_to(self, x, y):
        self.outer.emit_line_to(
            int(float(x) / self.base_scale),
            int(float(y) / self.base_scale))

    def emit_curve_to(self, x1, y1, x2, y2, x3, y3):
        self.outer.emit_curve_to(
            int(float(x1) / self.base_scale),
            int(float(y1) / self.base_scale),
            int(float(x2) / self.base_scale),
            int(float(y2) / self.base_scale),
            int(float(x3) / self.base_scale),
            int(float(y3) / self.base_scale))

    def emit_curve_to_s1(self, x2, y2, x3, y3):
        self.outer.emit_curve_to_s1(
            int(float(x2) / self.base_scale),
            int(float(y2) / self.base_scale),
            int(float(x3) / self.base_scale),
            int(float(y3) / self.base_scale))

    def emit_curve_to_s2(self, x1, y1, x3, y3):
        self.outer.emit_curve_to_s2(
            int(float(x1) / self.base_scale),
            int(float(y1) / self.base_scale),
            int(float(x3) / self.base_scale),
            int(float(y3) / self.base_scale))

    def emit_quadratic_curve_to(self, x1, y1, x2, y2):
        self.outer.emit_quadratic_curve_to(
            int(float(x1) / self.base_scale),
            int(float(y1) / self.base_scale),
            int(float(x2) / self.base_scale),
            int(float(y2) / self.base_scale))

    def emit_arc(self, rx, ry, phi, largeArc, sweep, x, y):
        self.outer.emit_arc(
            int(float(rx) / self.base_scale),
            int(float(ry) / self.base_scale),
            phi,
            largeArc,
            sweep,
            int(float(x) / self.base_scale),
            int(float(y) / self.base_scale))

    def emit_close_path(self):
        self.outer.emit_close_path()

    def emit_fill(self):
        self.outer.emit_fill()

    def emit_stroke(self):
        self.outer.emit_stroke()

    def emit_stroke_and_fill(self):
        self.outer.emit_stroke_and_fill()

class EmittingPathDataHandler(object):
    def __init__(self, emitter):
        self.emitter = emitter

    def close_path(self):
        self.emitter.emit_close_path()

    def move_to(self, x, y):
        self.emitter.emit_move_to(x, y)

    def line_to(self, x, y):
        self.emitter.emit_line_to(x, y)

    def curve_to(self, x1, y1, x2, y2, x, y):
        self.emitter.emit_curve_to(x1, y1, x2, y2, x, y)

    def curve_to_qb(self, x1, y1, x, y):
        self.emitter.emit_quadratic_curve_to(x1, y1, x, y)

    def arc(self, rx, ry, phi, largearc, sweep, x, y):
        self.emitter.emit_arc(rx, ry, phi, largearc, sweep, x, y)

class StyleNoneType(object):
    def __repr__(self):
        return 'StyleNone'

StyleNone = StyleNoneType()

class Style(object):
    __attrs__ = __slots__ = [
        'fill_color',
        'stroke_color',
        'stroke_width',
        'font_size',
        'font_family',
        'font_weight',
        'text_anchor',
        'text_align',
        'text_align_or_anchor',
        'line_height',
        ]

    def __init__(self, **kwargs):
        for key in self.__slots__:
            setattr(self, key, kwargs.get(key))

    def replace(self, **kwargs):
        params = {}
        return Style(
            **dict(
                (key, (kwargs.get(key) if kwargs.get(key) is not None else getattr(self, key)))
                for key in self.__slots__
                )
            )

    def __repr__(self):
        return 'Style(%s)' % ', '.join('%s=%r' % (k, getattr(self, k)) for k in self.__attrs__)

def text_and_elements(elem):
    if isinstance(elem, unicode):
        yield elem
    else:
        if elem.text:
            yield unicode(elem.text)
            elem.text = None
        for subelem in elem:
            yield subelem
            if subelem.tail:
                yield unicode(subelem.tail)
                subelem.tail = None

def namespace(ns):
    def decorator(f):
        f._visitor_namespace = ns
        return f
    return decorator

def transformable(f):
    def wrap(self, scanner, ns, local_name, elem):
        self.apply_transform(elem)
        f(self, scanner, ns, local_name, elem)
        self.unapply_transform()
    wrap._visitor_namespace = getattr(f, '_visitor_namespace', None)
    return wrap

def stylable(f):
    def wrap(self, scanner, ns, local_name, elem):
        self.apply_styles(elem)
        f(self, scanner, ns, local_name, elem)
        self.unapply_styles()
    wrap._visitor_namespace = getattr(f, '_visitor_namespace', None)
    return wrap

class StyleContext(object):
    def __init__(self, style, classes_pushed):
        self.style = style
        self.classes_pushed = classes_pushed

class Visitor(object):
    placeholder_pattern = ur'\ufeff{{((?:[^}]+|}[^}])*)}}\ufeff'

    def __init__(self, emitter, global_transform=None):
        self.emitter = emitter
        self.current_style_ctx = StyleContext(
            Style(fill_color=StyleNone,
                  stroke_color=StyleNone,
                  stroke_width=1,
                  font_size=12,
                  line_height=StyleNone,
                  text_anchor='start',
                  text_align='start'),
            {})
        self.style_stack = []
        self.current_transform = I
        self.transform_stack = []
        self.overloaded_classes = {}
        if global_transform is not None:
            self._apply_transform(global_transform)
        self.css_parser = cssutils.CSSParser()
        self.font_classes = {
            u"Arial": u"f0",
            u"Arial Black": u"f1",
            u"Verdana": u"f2",
            u"Impact": u"f3",
            u"Comic Sans MS": u"f4",
            u"Times New Roman": u"f5",
            u"Courier New": u"f6",
            u"Lucida Console": u"f7",
            u"Lucida Sans Unicode": u"f8",
            u"Modern": u"f9",
            u"Microsoft Sans Serif": u"f10",
            u"Roman": u"f11",
            u"Script": u"f12",
            u"Symbol": u"f13",
            u"Wingdings": u"f14",
            u"ＭＳ ゴシック": u"f15",
            u"MS Gothic": u"f15",
            u"ＭＳ Ｐゴシック": u"f16",
            u"MS PGothic": u"f16",
            u"ＭＳ 明朝": u"f17",
            u"MS Mincho": u"f17",
            u"ＭＳ Ｐ明朝": u"f18",
            u"MS PMincho": u"f18",
            u"MS UI Gothic": u"f19",
            }
        self.text_align_classes = {
            u"start": u"l",
            u"middle": u"c",
            u"end": u"r",
            }
        self.text_anchor_classes = {
            u"start": u"s",
            u"middle": u"m",
            u"end": u"e",
            }
        self.font_weight_classes = {
            u"900": u"b",
            u"bold": u"b",
            u"400": None,
            u"normal": None,
            }
        self.fixtag_placeholders = {
            u"発券日時": u"FIXTAG04",
            u"発券日時s": u"FIXTAG04",
            }
        self.text_align_map = {
            u"start": u"left",
            u"middle": u"center",
            u"end": u"right",
            u"left": u"left",
            u"center": u"center",
            u"right": u"right",
            }

    @staticmethod
    def parse_color_style(color):
        if color is None:
            return None
        elif color == u'none':
            return StyleNone
        else:
            return color

    def fetch_styles_from_element(self, elem):
        css_style_decl = self.css_parser.parseStyle(elem.get(u'style', ''), validate=False)

        stroke_color = self.parse_color_style(css_style_decl[u'stroke'] or elem.get(u'stroke'))
        stroke_width = as_user_unit(css_style_decl[u'stroke-width'] or elem.get(u'stroke-width'))
        fill_color = self.parse_color_style(css_style_decl[u'fill'] or elem.get(u'fill'))
        font_size = as_user_unit(css_style_decl['font-size'] or elem.get(u'font-size'), )
        font_family = css_style_decl['font-family'] or elem.get(u'font-family', None)
        font_weight = css_style_decl['font-weight'] or elem.get(u'font-weight', None)
        text_align = css_style_decl['text-align'] or elem.get(u'text-align')
        text_anchor = css_style_decl['text-anchor'] or elem.get(u'text-anchor')
        line_height = as_user_unit(css_style_decl['line-height'] or elem.get(u'line-height'), font_size or self.current_style_ctx.style.font_size)

        return self.current_style_ctx.style.replace(
            stroke_color=stroke_color,
            stroke_width=stroke_width,
            fill_color=fill_color,
            font_size=font_size,
            font_family=font_family,
            font_weight=font_weight,
            text_align=text_align,
            text_anchor=text_anchor,
            text_align_or_anchor=text_anchor or text_align,
            line_height=line_height
            )

    def _build_html_from_flow_elements(self, elems, container='div'):
        nodes = []
        for elem in elems:
            if isinstance(elem, basestring):
                elem = unicode(elem)
                lines = re.split(ur'\r\n|\r|\n', elem)
                for line in lines:
                    nodes.append(line)
            else:
                if elem.tag == u'{%s}flowSpan' % SVG_NAMESPACE:
                    tag = 'span'
                elif elem.tag == u'{%s}flowLine' % SVG_NAMESPACE:
                    tag = 'div'
                elif elem.tag == u'{%s}flowPara' % SVG_NAMESPACE:
                    tag = 'div'
                elif elem.tag == u'{%s}flowDiv' % SVG_NAMESPACE:
                    tag = 'div'
                else:
                    tag = None
                if tag is None:
                    raise Exception('Unsupported tag: %s' % elem.tag)

                html_styles = []

                line_height = None
                style = self.fetch_styles_from_element(elem)
                if self.current_style_ctx.style.line_height != style.line_height:
                    line_height = style.line_height

                if self.current_style_ctx.style.font_size != style.font_size:
                    html_styles.append((u'font-size', u'%gpx' % style.font_size))
                    # XXX: workaround to cope with the difference of
                    # interpretation of line-height between HTML and SVG
                    if line_height is None:
                        line_height = style.font_size
                if line_height is not None:
                    html_styles.append((u'line-height', u'%gpx' % line_height))
                if self.current_style_ctx.style.fill_color != style.fill_color:
                    if style.fill_color is not StyleNone:
                        html_styles.append((u'color', style.fill_color))
                if self.current_style_ctx.style.font_weight != style.font_weight:
                    html_styles.append((u'font-weight', style.font_weight))
                if self.current_style_ctx.style.text_align_or_anchor != style.text_align_or_anchor:
                    text_align = self.text_align_map.get(style.text_align_or_anchor.lower())
                    if text_align is not None:
                        html_styles.append((u'text-align', text_align))
                    else:
                        logger.warning("unknown text-align value: %s" % style.text_align_or_anchor)
                current_font_family_class = self.font_classes.get(self.current_style_ctx.style.font_family)
                if current_font_family_class is None:
                    # silenty falls back to the default font
                    current_font_family_class = u"f16"
                if style.font_family is not None:
                    new_font_family_class = self.font_classes.get(style.font_family)
                    if new_font_family_class is None:
                        logger.warning('Unsupported font %s; falling back to "f16"' % style.font_family)
                        new_font_family_class = u"f16"
                else:
                    new_font_family_class = current_font_family_class
                subelem = self._build_html_from_flow_elements(text_and_elements(elem), tag)
                if current_font_family_class != new_font_family_class:
                    subelem.set('class', new_font_family_class)
                if len(html_styles) > 0:
                    subelem.set('style', u';'.join(':'.join(pair) for pair in html_styles))
                if len(subelem.items()) == 0:
                    nodes.extend(text_and_elements(subelem))
                    if tag == 'div':
                        nodes.append(etree.Element('br'))
                else:
                    nodes.append(subelem)
        while len(nodes) > 0 and isinstance(nodes[-1], etree._Element) and nodes[-1].tag == 'br':
            nodes.pop()
        return E(container, *nodes)

    def build_html_from_flow_elements(self, elems):
        elems = list(elems)
        result = self._build_html_from_flow_elements(elems)
        retval = []
        if result.text:
            retval.append(unicode(result.text))
        for n in result:
            retval.append(etree.tostring(n, encoding=unicode, method='html'))
        return u''.join(retval)

    def _build_html_from_text_elements(self, elems, container='div'):
        nodes = []
        for elem in elems:
            if isinstance(elem, basestring):
                elem = unicode(elem)
                lines = re.split(ur'\r\n|\r|\n', elem)
                for line in lines:
                    line = line.strip()
                    if line:
                        nodes.append(line)
            else:
                if elem.tag == u'{%s}tspan' % SVG_NAMESPACE:
                    tag = 'span'
                else:
                    raise Exception('Unsupported tag: %s' % elem.tag)

                html_styles = []

                line_height = None
                style = self.fetch_styles_from_element(elem)
                if self.current_style_ctx.style.line_height != style.line_height:
                    line_height = style.line_height

                if self.current_style_ctx.style.font_size != style.font_size:
                    html_styles.append((u'font-size', u'%gpx' % style.font_size))
                    # XXX: workaround to cope with the difference of
                    # interpretation of line-height between HTML and SVG
                    if line_height is None:
                        line_height = style.font_size
                if line_height is not None:
                    html_styles.append((u'line-height', u'%gpx' % line_height))
                if self.current_style_ctx.style.fill_color != style.fill_color:
                    html_styles.append((u'color', style.fill_color))
                if self.current_style_ctx.style.font_weight != style.font_weight:
                    html_styles.append((u'font-weight', style.font_weight))
                current_font_family_class = self.font_classes.get(self.current_style_ctx.style.font_family)
                if current_font_family_class is None:
                    # silenty falls back to the default font
                    current_font_family_class = u"f16"
                if style.font_family is not None:
                    new_font_family_class = self.font_classes.get(style.font_family)
                    if new_font_family_class is None:
                        logger.warning('Unsupported font %s; falling back to "f16"' % style.font_family)
                        new_font_family_class = u"f16"
                else:
                    new_font_family_class = current_font_family_class
                subelem = self._build_html_from_text_elements(text_and_elements(elem), tag)
                if current_font_family_class != new_font_family_class:
                    subelem.set('class', new_font_family_class)
                if len(html_styles) > 0:
                    subelem.set('style', u';'.join(':'.join(pair) for pair in html_styles))
                if len(subelem.items()) == 0:
                    nodes.extend(text_and_elements(subelem))
                else:
                    nodes.append(subelem)
        return E(container, *nodes)

    def build_html_from_text_elements(self, elems):
        elems = list(elems)
        result = self._build_html_from_text_elements(elems)
        retval = []
        if result.text:
            retval.append(unicode(result.text))
        for n in result:
            retval.append(etree.tostring(n, encoding=unicode, method='html'))
        return u''.join(retval)

    def emit_styles(self, old_style, new_style):
        if new_style.fill_color != old_style.fill_color:
            self.emitter.emit_fill_color(new_style.fill_color if new_style.fill_color is not StyleNone else 0)
        if new_style.stroke_color != old_style.stroke_color:
            self.emitter.emit_stroke_color(new_style.stroke_color if new_style.stroke_color is not StyleNone else 0)
        if new_style.stroke_width != old_style.stroke_width:
            self.emitter.emit_stroke_width(new_style.stroke_width if new_style.stroke_width is not StyleNone else 0)
        if new_style.font_size != old_style.font_size:
            self.emitter.emit_font_size((new_style.font_size if new_style.font_size is not StyleNone else 0))
        if self.current_style_ctx.style.line_height != new_style.line_height:
            self.emitter.emit_line_height((new_style.line_height if new_style.line_height is not StyleNone else 0))


    def emit_transform(self, old_transform, new_transform):
        if not numpy.array_equal(old_transform, new_transform):
            self.emitter.emit_transform(
                new_transform[0, 0],
                new_transform[1, 0],
                new_transform[0, 1],
                new_transform[1, 1],
                new_transform[0, 2],
                new_transform[1, 2]
                )

    def apply_styles(self, elem):
        self.style_stack.append(self.current_style_ctx)
        new_style = self.fetch_styles_from_element(elem)
        self.emit_styles(self.current_style_ctx.style, new_style)

        classes_pushed = {}

        if new_style.font_family is not None:
            font_family_class = self.font_classes.get(new_style.font_family)
            if font_family_class is None:
                logger.warning('Unsupported font %s; falling back to "f16"' % new_style.font_family)
                font_family_class = u"f16"
            old_font_family_class = self.font_classes.get(self.current_style_ctx.style.font_family)
            if font_family_class != old_font_family_class:
                classes_pushed['font_family'] = font_family_class

        if new_style.font_weight is not None:
            if new_style.font_weight not in self.font_weight_classes:
                logger.warning('Unsupported font weight %s; falling back to "normal"' % new_style.font_weight)
                font_weight_class = None
            else:
                font_weight_class = self.font_weight_classes[new_style.font_weight]
            if font_weight_class is not None:
                old_font_weight_class = self.font_weight_classes.get(self.current_style_ctx.style.font_weight)
                if font_weight_class != old_font_weight_class:
                    classes_pushed['font_weight'] = font_weight_class

        if elem.tag not in (u'{%s}text' % SVG_NAMESPACE, u'{%s}tspan' % SVG_NAMESPACE):
            if new_style.text_align_or_anchor is not None:
                text_align_class = self.text_align_classes.get(new_style.text_align_or_anchor)
                old_text_align_class = self.text_align_classes.get(self.current_style_ctx.style.text_align_or_anchor)
                if text_align_class is None:
                    logger.warning('Unsupported align type %s; falling back to start' % new_style.text_align_or_anchor)
                    text_align_class = u"l"
                if text_align_class != old_text_align_class:
                    classes_pushed['text_align'] = text_align_class

        stack_level = None
        for k, l in self.overloaded_classes.items():
            if k in classes_pushed:
                if stack_level is None or stack_level > l:
                    stack_level = l

        if stack_level is not None:
            i = len(self.style_stack)
            while i > stack_level:
                i -= 1
                style_ctx = self.style_stack[i]
                prev_classes_pushed = style_ctx.classes_pushed
                for _ in range(0, len(prev_classes_pushed)):
                    self.emitter.emit_pop_class()
                if i == stack_level:
                    _classes_pushed = dict(prev_classes_pushed)
                    _classes_pushed.update(classes_pushed)
                    classes_pushed = _classes_pushed
                prev_classes_pushed.clear()

        for k, v in classes_pushed.items():
            self.overloaded_classes[k] = len(self.style_stack)
            self.emitter.emit_push_class(v)

        self.current_style_ctx = StyleContext(new_style, classes_pushed)

    def unapply_styles(self):
        prev_style_ctx = self.style_stack.pop()
        for _ in range(0, len(self.current_style_ctx.classes_pushed)):
            self.emitter.emit_pop_class()

        if prev_style_ctx.style.line_height is not None and self.current_style_ctx.style.line_height != prev_style_ctx.style.line_height:
            self.emitter.emit_line_height(prev_style_ctx.style.line_height)
        self.emit_styles(self.current_style_ctx.style, prev_style_ctx.style)
        self.current_style_ctx = prev_style_ctx

    def apply_transform(self, elem):
        self.transform_stack.append(self.current_transform)
        transform_str = elem.get(u'transform', None)
        if transform_str != None:
            self._apply_transform(parse_transform(transform_str))

    def _apply_transform(self, matrix):
        new_transform = self.current_transform * matrix
        self.emit_transform(self.current_transform, new_transform)
        self.current_transform = new_transform

    def unapply_transform(self):
        prev_transform = self.transform_stack.pop()
        self.emit_transform(self.current_transform, prev_transform)
        self.current_transform = prev_transform

    def emit_fill_stroke(self):
        if self.current_style_ctx.style.fill_color is not StyleNone:
            if self.current_style_ctx.style.stroke_color is not StyleNone:
                self.emitter.emit_stroke_and_fill()
            else:
                self.emitter.emit_fill()
        elif self.current_style_ctx.style.stroke_color is not StyleNone:
            self.emitter.emit_stroke()

    @namespace(SVG_NAMESPACE)
    @stylable
    @transformable
    def visit_path(self, scanner, ns, local_name, elem):
        path = elem.get(u'd')
        if path is None:
            raise Exception("No `d' attribute for path")
        self.emitter.emit_new_path()
        PathDataScanner(
            tokenize_path_data(path),
            EmittingPathDataHandler(self.emitter))()
        self.emit_fill_stroke()

    @namespace(SVG_NAMESPACE)
    @stylable
    @transformable
    def visit_rect(self, scanner, ns, local_name, elem):
        x = as_user_unit(elem.get(u'x', u'0'))
        y = as_user_unit(elem.get(u'y', u'0'))
        width = as_user_unit(elem.get(u'width', u'0'))
        height = as_user_unit(elem.get(u'height', u'0'))
        rx = as_user_unit(elem.get(u'rx', u'0'))
        ry = as_user_unit(elem.get(u'ry', u'0'))
        self.emitter.emit_new_path()
        if rx == 0 and ry == 0:
            self.emitter.emit_move_to(x, y)
            self.emitter.emit_line_to(x + width, y)
            self.emitter.emit_line_to(x + width, y + height)
            self.emitter.emit_line_to(x, y + height)
            self.emitter.emit_line_to(x, y)
            self.emitter.emit_close_path()
        else:
            self.emitter.emit_move_to(x + rx, y)
            self.emitter.emit_line_to(x + width - rx, y)
            self.emitter.emit_arc(rx, ry, 0., False, True, x + width, y + ry)
            self.emitter.emit_line_to(x + width, y + height - ry)
            self.emitter.emit_arc(rx, ry, 0., False, True, x + width - rx, y + height)
            self.emitter.emit_line_to(x + rx, y + height)
            self.emitter.emit_arc(rx, ry, 0., False, True, x, y + height - ry)
            self.emitter.emit_line_to(x, y + ry)
            self.emitter.emit_arc(rx, ry, 0., False, True, x + rx, y)
            self.emitter.emit_close_path()
        self.emit_fill_stroke()

    @namespace(SVG_NAMESPACE)
    @stylable
    @transformable
    def visit_circle(self, scanner, ns, local_name, elem):
        cx = as_user_unit(elem.get(u'cx', u'0'))
        cy = as_user_unit(elem.get(u'cy', u'0'))
        r = as_user_unit(elem.get(u'r', u'0'))
        self.emitter.emit_new_path()
        self.emitter.emit_move_to(cx + r, y)
        self.emitter.emit_arc(r, r, False, False, True, cx + r, cy)
        self.emitter.emit_close_path()
        self.emit_fill_stroke()

    @namespace(SVG_NAMESPACE)
    @stylable
    @transformable
    def visit_flowRegion(self, scanner, ns, local_name, elem):
        children = list(elem)
        if len(children) != 1 or children[0].tag != u'{%s}rect' % SVG_NAMESPACE:
            raise Exception('flowRegion must contain only one element and it must be <rect>')
        rect = children[0]
        self.flow_bbox = (
            as_user_unit(rect.get(u'x', u'0')),
            as_user_unit(rect.get(u'y', u'0')),
            as_user_unit(rect.get(u'width', u'0')),
            as_user_unit(rect.get(u'height', u'0'))
            )

    def _strip_placeholders(self, text):
        return re.sub(self.placeholder_pattern, u'', text)

    def _text_block_html_emitter(self, flow_bbox, html): 
        emission = None
        g = re.match(self.placeholder_pattern + u'$', html)
        if g is not None:
            path = self.fixtag_placeholders.get(g.group(1))
            if path is not None:
                def emission():
                    self.emitter.emit_show_dom_node_text_block(flow_bbox[2], flow_bbox[3], path)
        else:
            def emission():
                self.emitter.emit_show_text_block(flow_bbox[2], flow_bbox[3], self._strip_placeholders(html))
        return emission

    def _text_html_emitter(self, anchor, html): 
        emission = None
        g = re.match(self.placeholder_pattern + u'$', html)
        if g is not None:
            path = self.fixtag_placeholders.get(g.group(1))
            if path is not None:
                def emission():
                    self.emitter.emit_show_dom_node_text(anchor, path)
        else:
            def emission():
                self.emitter.emit_show_text(anchor, self._strip_placeholders(html))
        return emission

    @namespace(SVG_NAMESPACE)
    @stylable
    @transformable
    def visit_flowRoot(self, scanner, ns, local_name, elem):
        flow_region_visited = False
        flow_div_visited = False
        contents = []
        for n in elem:
            if n.tag == u'{%s}flowRegion' % SVG_NAMESPACE:
                if flow_region_visited:
                    raise Exception('<flowRoot> contains more than one <flowRegion>')
                self.visit_flowRegion(scanner, ns, local_name, n)
                flow_region_visited = True
            elif n.tag == u'{%s}flowPara' % SVG_NAMESPACE:
                contents.append(n)
            elif n.tag == u'{%s}flowDiv' % SVG_NAMESPACE:
                contents.append(n)

        if not flow_region_visited:
            raise Exception('<flowRoot> contains no <flowRegion>')

        if contents:
            singleton_elems = len(contents) == 1 and singletons(contents[0])
            if singleton_elems:
                emission = self._text_block_html_emitter(self.flow_bbox, self.build_html_from_flow_elements(text_and_elements(singleton_elems[-1])))
                # Specially treat a sole container element :-p
                if emission:
                    self.emitter.emit_move_to(self.flow_bbox[0], self.flow_bbox[1])
                    for elem in singleton_elems:
                        self.apply_styles(elem)
                    emission()
                    for _ in singleton_elems:
                        self.unapply_styles()
            else:
                emission = self._text_block_html_emitter(self.flow_bbox, self.build_html_from_flow_elements(contents))
                if emission:
                    self.emitter.emit_move_to(self.flow_bbox[0], self.flow_bbox[1])
                    emission()

    @namespace(SVG_NAMESPACE)
    @stylable
    @transformable
    def visit_text(self, scanner, ns, local_name, elem):
        pos = (
            as_user_unit(elem.get(u'x', u'0')),
            as_user_unit(elem.get(u'y', u'0')),
            )
        style = self.current_style_ctx.style
        anchor = self.text_anchor_classes.get(style.text_anchor)
        if anchor is None:
            logger.warning("unknown text-anchor value: %s" % style.text_anchor)
            anchor = self.text_anchor_classes['start']
        emission = self._text_html_emitter(anchor, self.build_html_from_text_elements(text_and_elements(elem)))
        if emission:
            self.emitter.emit_move_to(pos[0], pos[1])
            emission()

    @namespace(SVG_NAMESPACE)
    @stylable
    @transformable
    def visit_g(self, scanner, ns, local_name, elem):
        scanner(elem)

    @namespace(SVG_NAMESPACE)
    def visit_svg(self, scanner, ns, local_name, elem):
        scanner(elem)

    def _visit_default(self, scanner, ns, local_name, elem):
        pass

class Scanner(object):
    def __init__(self, visitor):
        self.re = re.compile('^(?:{([^}]*)})(.*)')
        self.visitor = visitor

    def __call__(self, elems):
        for elem in elems:
            groups = re.match(self.re, elem.tag)
            if groups:
                ns = groups.group(1)
                local_name = groups.group(2)
            else:
                ns = None
                local_name = elem.tag
            f_name = 'visit_' + local_name
            f = getattr(self.visitor, f_name, None)
            if f is None or not getattr(f, '_visit_namespace', None) in (None, ns):
                f = self.visitor._visit_default
            f(self, ns, local_name, elem)

def determine_qrcode_type(qrcode_content):
    if not re.match(r'[^0-9]', qrcode_content):
        return 1
    if not re.match(r'[^0-9A-Z $%*+./:-]', qrcode_content):
        return 2
    i = iter(qrcode_content.encode('CP932'))
    try:
        while True:
            c = ord(i.next())
            if (c >= 0x81 and c <= 0x9f) or (c >= 0xe0 and c <= 0xfe):
                i.next()
            else:
                return 4
    except StopIteration:
        pass
    return 3

def determine_level_and_cell_size(width, height, ectype, qrcode_type, qrcode_content):
    table = QR_LEVEL_TABLES[qrcode_type - 1][ectype == 'H']
    l = len(qrcode_content)
    level = None
    import sys
    for level, _l in enumerate(table):
        if l <= _l:
            break
    else:
        raise Exception('No suitable QR code level found: content too long? - %s' % qrcode_content)
    calculated_width = None
    cell_size = None
    width = min(24.2, width)
    height = min(24.2, height)
    for cell_size in (6, 5, 4):
        cell_size_in_mm = 1.3552 * cell_size / 4
        calculated_width = (level + 5 + .25 + 1) * cell_size_in_mm
        if calculated_width <= width and calculated_width <= height:
            break
    else:
        raise Exception('No suitable cell size found: drawing area too small? (%g, %g) > (%g, %g)' % (calculated_width, calculated_width, width, height))
    return level, cell_size   

def handle_qrcode(retval, qrcode):
    content = qrcode.get('content')
    width = as_user_unit(qrcode.get('width'))
    height = as_user_unit(qrcode.get('height'))
    type_ = determine_qrcode_type(content)
    ectype = SEJ_ECLEVEL_MAP.get(qrcode.get('eclevel', 'h').lower(), 'Q')
    level, cell_size = determine_level_and_cell_size(width, height, ectype, type_, content)
    retval.append(E.QR_DATA(content))
    retval.append(E.QR_CHAR('%d' % type_))
    retval.append(E.QR_ERR(ectype))
    retval.append(E.QR_VER(u'%02d' % (level + 1)))
    retval.append(E.QR_CELL('%d' % cell_size))

def to_opcodes(doc, global_transform=None, notation_version=1):
    opcodes = []
    emitter = ScaleFilter(Assembler(opcodes), .1)
    emitter.emit_unit('px')
    Scanner(Visitor(emitter, global_transform))([doc.getroot()])
    opcodes = Optimizer()(opcodes)
    result = []
    emit_opcodes(TicketNotationEmitter(result, notation_version), opcodes)
    return result

def convert_svg(doc, global_transform=None, notation_version=None):
    if notation_version is None:
        notation_version = 1
    retval = E.TICKET(
        E.b(u' '.join(to_opcodes(doc, global_transform, notation_version))), 
        E.FIXTAG01(),
        E.FIXTAG02(),
        E.FIXTAG03(),
        E.FIXTAG04(),
        E.FIXTAG05(),
        E.FIXTAG06(),
        E.FIXTAG07())
    qrcode = doc.find('{%s}qrcode' % TS_SVG_EXT_NAMESPACE)
    if qrcode is not None:
        handle_qrcode(retval, qrcode)

    return retval

if __name__ == '__main__':
    import sys
    from altair.app.ticketing.tickets.cleaner import cleanup_svg
    tree = etree.parse(sys.stdin)
    cleanup_svg(tree)
    print re.sub(r'''encoding=(["'])Windows-31J\1''', 'encoding="Shift_JIS"', etree.tostring(convert_svg(tree, parse_transform(sys.argv[1]) if len(sys.argv) >= 2 else None), encoding='Windows-31J'))
