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
        layout = Layout(template_filename=self.get_basename(params), 
                        title=params["title"], 
                        blocks=blocks)
        return layout

    def create(self, params):
        filesession = get_layout_filesession(self.request)
        prefixed_name = os.path.join(self.organization.short_name,self.get_basename(params))
        filedata = File(name=prefixed_name, handler=params["filepath"].file)
        filesession.add(filedata)

        blocks = self.get_blocks(params)
        layout = self.create_model(params, blocks)
        DBSession.add(layout)

        ## todo:moveit
        filesession.commit()

        notify_model_create(self.request, layout, params)
        return layout
