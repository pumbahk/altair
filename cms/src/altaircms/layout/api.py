import os
from zope.interface import implementer
from .interfaces import ILayoutCreator
from pyramid.path import AssetResolver

def get_layout_creator(request):
    return request.registry.getUtility(ILayoutCreator)

class LayoutFormProxy(object):
    def __getattr__(self, k, default=None):
        return getattr(self.form, k, default)

    def __init__(self, template_path, form):
        self.template_path = template_path
        self.form = form

    def validate(self):
        return True

@implementer(ILayoutCreator)
class LayoutCreator(object):
    """
    params = {
      title: "fooo", 
      file: "file field object", 
      blocks: "" #auto detect
    }
    """
    def __init__(self, template_path):
        self.assetresolver = AssetResolver()
        self.template_path = self.assetresolver.resolve(template_path).abspath()

    def as_form_proxy(self, form):
        return LayoutFormProxy(self.template_path, form)

    def get_basename(self, params):
        return os.path.basename(params["filepath"].filename)

    def get_filename(self, params):
        return os.path.join(self.template_path, self.get_basename(params))

    def get_buf(self, params):
        return params["filepath"].file

    def create_file(self, params):
        filename = self.get_filename(params)
        buf = self.get_buf(params)

        with open(filename, "w+b") as wf:
            buf.seek(0)
            while 1:
                data = buf.read(26)
                if not data:
                    break
                wf.write(data)

    def get_blocks(self, params):
        return "[]"

    def create_model(self, params):
        from altaircms.layout.models import Layout
        layout = Layout(template_filename=self.get_basename(params), 
                        title=params["title"], 
                        blocks=self.get_blocks(params))
        return layout
