from collections import namedtuple

Size = namedtuple('Size', 'width height')

from .convert import as_user_unit

def extract_paper_size(ticket_format):
    size = ticket_format.data['size']
    return Size(as_user_unit(size['width']), as_user_unit(size['height']))

def user_unit_in_mm(v):
    return v * 25.4 / 90

def format_size(size):
    return '%dmm x %dmm' % (user_unit_in_mm(size.width), user_unit_in_mm(size.height))
