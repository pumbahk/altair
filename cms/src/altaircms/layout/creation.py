import os
import json

from zope.interface import implementer
import logging
logger = logging.getLogger(__name__)
from pyramid.path import AssetResolver

from mako.lexer import Lexer
from mako.parsetree import BlockTag

from .interfaces import ILayoutCreator
from .models import Layout

class LayoutFormProxy(object):
    def __getattr__(self, k, default=None):
        return getattr(self.form, k, default)

    def __init__(self, template_path, form):
        self.template_path = template_path
        self.form = form

    def validate(self):
        return True

def collect_block_name_from_makotemplate(text):
    nodes = _collect_block_node_from_makotemplate(text)
    return [n.name for n in nodes]

def _collect_block_node_from_makotemplate(text):
    r = []
    def _traverse(node):
        if hasattr(node, "nodes"):
            for n in node.nodes:
                _traverse(n)
        if isinstance(node, BlockTag):
            r.append(node)
    _traverse(Lexer(text, input_encoding="utf-8").parse())
    return r

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
        self.template_path_asset_spec = template_path
        self.template_path = self.assetresolver.resolve(template_path).abspath()

    def as_form_proxy(self, form):
        return LayoutFormProxy(self.template_path, form)

    def get_basename(self, params):
        return os.path.basename(params["filepath"].filename)

    def get_filename(self, params):
        if "prefix" in params: #xxx:
            return os.path.join(self.template_path, params["prefix"],  self.get_basename(params))            
        else:
            return os.path.join(self.template_path, self.get_basename(params))

    def get_layout_filepath(self, layout):
        return os.path.join(self.template_path, layout.prefixed_template_filename)

    def get_buf(self, params):
        buf = params["filepath"].file
        buf.seek(0)
        return buf

    def create_file(self, params):
        filename = self.get_filename(params)
        buf = self.get_buf(params)
        logger.info("*create layout* create layout path: %s" % filename)
        with open(filename, "w+b") as wf:
            while 1:
                data = buf.read(26)
                if not data:
                    break
                wf.write(data)

    def get_blocks(self, params):
        buf = self.get_buf(params)
        block_names = collect_block_name_from_makotemplate(buf.read())
        return json.dumps([[name] for name in block_names])

    def create_model(self, params):
        layout = Layout(template_filename=self.get_basename(params), 
                        title=params["title"], 
                        blocks=self.get_blocks(params))
        return layout
