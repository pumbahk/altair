# encoding: utf-8

import logging
import sqlalchemy as sa

from .utils import Size
from .convert import as_user_unit
from .constants import *

def extract_paper_size(ticket_format):
    size = ticket_format.data['size']
    return Size(as_user_unit(size['width']), as_user_unit(size['height']))

def extract_perforations(ticket_format):
    perforations = ticket_format.data.get("perforations")
    if not perforations:
        return {"vertical": [], "horizontal": []}
    else:
        return perforations

def extract_printable_areas(ticket_format):
    return ticket_format.data["printable_areas"]

def extract_orientation(page_format):
    return page_format.data["orientation"]

def format_orientation(orientation):
    return [u'タテ', u'ヨコ'][ORIENTATIONS.index(orientation)]

def extract_paper(page_format):
    return page_format.data.get(u"paper")

def format_paper_name(paper_id):
    return PAPERS[paper_id] if paper_id is not None else u'(設定なし)'

def extract_printable_area(page_format):
    return page_format.data["printable_area"]

def format_rectangle(rect):
    return u'左上端からの位置: %(x)s, %(y)s<br />幅 / 高さ: %(width)s x %(height)s' % rect

def extract_ticket_margin(page_format):
    return page_format.data["ticket_margin"]

def format_orientation(orientation):
    return [u'タテ', u'ヨコ'][ORIENTATIONS.index(orientation)]

def extract_ticket_margin(page_format):
    return page_format.data['ticket_margin']

def format_margin(margin):
    return u'上: %(top)s 下: %(bottom)s 左: %(left)s 右: %(right)s' % margin

def user_unit_in_mm(v):
    return v * 25.4 / 90

def format_size(size):
    return '%dmm x %dmm' % (user_unit_in_mm(size.width), user_unit_in_mm(size.height))


## sortable, 
def sortparams(prefix, request, defaults=(None, None)):
    sort_by = request.params.get(prefix + '_sort', None)
    direction = request.params.get(prefix + '_direction', None)
    if (sort_by is None or sort_by == '') and not direction:
        return defaults
    return sort_by, direction

def sortable(prefix, request, sort_by, direction="asc", **kwargs):
    defaults = request.params.copy()
    _sort_by, _direction = sortparams(prefix, request)
    if sort_by == _sort_by:
        direction = 'desc' if _direction == 'asc' else 'asc'
    defaults.update({ prefix + '_sort': sort_by, prefix + '_direction': direction })
    defaults.update(kwargs)
    url = request.current_route_url(_query=defaults)
    return url

def get_direction(direction):
    if direction == "asc":
        return sa.asc
    elif direction == "desc":
        return sa.desc
    else:
        logging.debug("unexcepted direction %s" % direction)
        return sa.asc
    
