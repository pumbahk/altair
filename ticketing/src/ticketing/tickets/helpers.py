from collections import namedtuple
import logging
import sqlalchemy as sa

Size = namedtuple('Size', 'width height')
from .convert import as_user_unit

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
    printable_areas = ticket_format.data.get("printable_areas")
    if not printable_areas:
        return {"vertical": [], "horizontal": []}
    else:
        return printable_areas
    
def user_unit_in_mm(v):
    return v * 25.4 / 90

def format_size(size):
    return '%dmm x %dmm' % (user_unit_in_mm(size.width), user_unit_in_mm(size.height))


## sortable, 
def sortable(request, name, direction="asc", **kwargs):
    defaults = request.params.copy()
    defaults.update(sort=name, direction=direction)
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
    
