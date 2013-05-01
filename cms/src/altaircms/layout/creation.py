import os
import json
import logging
logger = logging.getLogger(__name__)

from ..models import DBSession
from ..subscribers import notify_model_create
from .models import Layout
from .collectblock import collect_block_name_from_makotemplate

from . import SESSION_NAME
from ..filelib import get_adapts_filesession, File

def get_layout_filesession(request):
    return get_adapts_filesession(request, name=SESSION_NAME)

def is_file_field(field):
    return hasattr(field, "file") and hasattr(field, "filename")

def get_filename(inputname, filename):
    if not inputname:
        return filename
    dirname, _ = os.path.splitext(inputname)
    return dirname+os.path.splitext(filename)[1]
        

class LayoutWriter(object):
    def __init__(self, request):
        self.request = request
        self.filesession = get_layout_filesession(self.request)

    def write_layout_file(self, basename, organization,  params):
        prefixed_name = os.path.join(organization.short_name, basename)
        filedata = File(name=prefixed_name, handler=params["filepath"].file)
        self.filesession.add(filedata)

    def commit(self, *args, **kwargs):
        return self.filesession.commit(*args, **kwargs)

class LayoutInfoDetector(object):
    """
    params = {
      title: "fooo", 
      file: "file field object", 
      blocks: "" #auto detect
    }
    """
    def __init__(self, request):
        self.request = request

    def get_blocks(self, params):
        buf = params["filepath"].file
        pos = buf.tell()
        buf.seek(0)
        block_names = collect_block_name_from_makotemplate(buf.read())
        buf.seek(pos)
        return json.dumps([[name] for name in block_names])

    def get_basename(self, params):
        return get_filename(params.get("template_filename"),
                            os.path.basename(params["filepath"].filename))
    

class LayoutCreator(object):
    def __init__(self, request, organization):
        self.request = request
        self.organization = organization
        self.writer = LayoutWriter(request)
        self.detector = LayoutInfoDetector(request)

    def create_model(self, basename, params, blocks):
        layout = Layout(template_filename=basename, 
                        title=params["title"], 
                        blocks=blocks)
        DBSession.add(layout)
        return layout

    def create(self, params, pagetype_id):
        try:
            basename = self.detector.get_basename(params)
            self.writer.write_layout_file(basename, self.organization, params)
            blocks = self.detector.get_blocks(params)
            layout = self.create_model(basename, params, blocks)
            layout.pagetype_id = pagetype_id
            notify_model_create(self.request, layout, params)
            self.writer.commit([layout])
            return layout
        except Exception, e:
            logger.exception(str(e))

class LayoutUpdater(object):
    def __init__(self, request, organization):
        self.request = request
        self.organization = organization
        self.writer = LayoutWriter(request)
        self.detector = LayoutInfoDetector(request)

    def update_model(self, layout, filename, params, blocks):
        layout.title =params["title"]
        layout.blocks = blocks
        layout.template_filename = filename
        DBSession.add(layout)
        return layout

    def update(self, layout, params, pagetype_id):
        try:
            if is_file_field(params["filepath"]):
                basename = self.detector.get_basename(params)
                self.writer.write_layout_file(basename, self.organization, params)
                blocks = self.detector.get_blocks(params)
            else:
                basename = layout.template_filename
                blocks = params["blocks"]
            layout = self.update_model(layout, basename, params, blocks)
            layout.pagetype_id = pagetype_id
            self.writer.commit([layout])
            return layout
        except Exception, e:
            logger.error(str(e))
