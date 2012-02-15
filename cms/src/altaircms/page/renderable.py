import json

def _safe_json_loads(string):
    if not isinstance(string, basestring):
        return string
    if isinstance(string, unicode):
        string = string.encode("utf-8")
    return json.loads(string)
    
class LayoutImage(object):
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

