import re

def is_drawing_compressed(drawing):
    return re.match('^.+\.(svgz|gz)$', drawing.path)
