# -*- coding:utf-8 -*-

import json

def _safe_json_loads(string):
    if string is None:
        return []
    if not isinstance(string, basestring):
        return string
    if isinstance(string, unicode):
        string = string.encode("utf-8")
    return json.loads(string)
    
class BlocksImage(object):
    """ use this in template
    % for name in layout_image:
      <div id="${name}">${name}</div>
    % endfor
    """
    @classmethod
    def from_json(cls, json):
        return cls(_safe_json_loads(json))

    def __init__(self, structure):
        self.structure = structure

    def __iter__(self):
        for row in self.structure:
            for x in row:
                yield x

class LayoutRender(object):
    def __init__(self, layout):
        self.obj = layout

    def blocks_image(self):
        return BlocksImage.from_json(self.obj.blocks)
