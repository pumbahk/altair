# -*- coding:utf-8 -*-

import json
import altaircms.helpers as helpers

def _safe_json_loads(string):
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

class PageRender(object):
    def __init__(self, page):
        self.obj = page

    def publish_status(self, request=None):
        if self.obj.is_published():
            return u"公開中"
        elif request:
            link_url = helpers.front.to_preview_page(request, self.obj)
            return u'非公開(%s)' % helpers.base.make_link(u"preview", link_url)
        else:
            return u"非公開"

