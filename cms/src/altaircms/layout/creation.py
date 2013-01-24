import os
import json
import logging
logger = logging.getLogger(__name__)

from ..models import DBSession
from ..subscribers import notify_model_create
from .models import Layout
from .collectblock import collect_block_name_from_makotemplate

from . import SESSION_NAME
from ..filelib import get_filesession, File

def get_layout_filesession(request):
    return get_filesession(request, name=SESSION_NAME)

def is_file_field(field):
    return hasattr(field, "file") and hasattr(field, "filename")

class LayoutCreator(object):
    """
    params = {
      title: "fooo", 
      file: "file field object", 
      blocks: "" #auto detect
    }
    """
    def __init__(self, request, organization):
        self.request = request
        self.organization = organization
        
    def get_blocks(self, params):
        buf = params["filepath"].file
        pos = buf.tell()
        buf.seek(0)
        block_names = collect_block_name_from_makotemplate(buf.read())
        buf.seek(pos)
        return json.dumps([[name] for name in block_names])

    def get_basename(self, params):
        return os.path.basename(params["filepath"].filename)

    def create_model(self, params, blocks):
        basename = params.get("template_filename") or self.get_basename(params)
        layout = Layout(template_filename=basename, 
                        title=params["title"], 
                        blocks=blocks)
        DBSession.add(layout)
        return layout

    def update_model(self, layout, params, blocks):
        layout.title =params["title"]
        layout.blocks = blocks
        layout.template_filename = params.get("template_filename") or self.get_basename(params)
        DBSession.add(layout)
        return layout

    def write_layout_file(self, params):
        filesession = get_layout_filesession(self.request)
        basename = params.get("template_filename") or self.get_basename(params)
        prefixed_name = os.path.join(self.organization.short_name, basename)
        filedata = File(name=prefixed_name, handler=params["filepath"].file)
        filesession.add(filedata)

        ## todo:moveit
        filesession.commit()
        return 

    def create(self, params):
        self.write_layout_file(params)
        blocks = self.get_blocks(params)
        layout = self.create_model(params, blocks)
        notify_model_create(self.request, layout, params)
        return layout

    def update(self, layout, params):
        if is_file_field(params["filepath"]):
            self.write_layout_file(params)
            blocks = self.get_blocks(params)
        else:
            blocks = params["blocks"]
        layout = self.update_model(layout, params, blocks)
        return layout
