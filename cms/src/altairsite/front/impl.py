# -*- coding:utf-8 -*-
from zope.interface import Interface
from zope.interface import implementer
from pyramid.path import AssetResolver
import logging
logger = logging.getLogger(__name__)
import os

class ILayoutTemplateLookUp(Interface):
    def from_layout(layout):
        """ this is layout model"""
    def from_file(filename):
        """lookup template instance"""

@implementer(ILayoutTemplateLookUp)
class LayoutTemplate(object):
    def __init__(self, layout_spec, default_prefix="default"):
        self.layout_spec = layout_spec
        resolved = AssetResolver().resolve(layout_spec)
        if not resolved.exists():
            os.mkdir(resolved.abspath())
        self.layoutdir = resolved.abspath()
        self.default_prefix = default_prefix
    
    def from_layout_default(self, request, layout):
        filename_default = os.path.join(self.default_prefix, layout.template_filename)
        logger.debug("layout template is not found. search %s" % (filename_default))
        return filename_default

    def from_layout(self, request, layout):
        return layout.prefixed_template_filename

    def exists(self, filename):
        return os.path.exists(self.abspath(filename))

    def abspath(self, filename):
        return os.path.join(self.layoutdir, filename)

    def as_layout_spec(self, filename):
        return os.path.join(self.layout_spec, filename)

    def get_renderable_template(self, request, layout, verbose=False):
        layout_filename = self.from_layout(request, layout)
        if self.exists(layout_filename):
            return self.as_layout_spec(layout_filename)
        if verbose:
            logger.info("layout template file %s is not found. lookup in default template path" % self.abspath(layout_filename))
        layout_filename = self.from_layout_default(request, layout)
        if verbose:
            logger.info("default template path %s is" % self.abspath(layout_filename))
        if self.exists(layout_filename):
            return self.as_layout_spec(layout_filename)
        return None

