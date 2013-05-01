# -*- coding:utf-8 -*-
from zope.interface import Interface
from zope.interface import implementer
from pyramid.path import AssetResolver
import logging
logger = logging.getLogger(__name__)
import os

class ILayoutModelResolver(Interface):
    def resolve(request, layout):
        pass

class ILayoutModelDescriptor(Interface):
    """minisize of pyramid.AssetDescriptor"""
    def abspath():
        pass

    def exists():
        pass

    def absspec():
        pass

@implementer(ILayoutModelDescriptor)
class LayoutModelDescriptor(object):
    def __init__(self, layout_spec, layoutdir, filename, checkskip=False, layout=None):
        self.layout_spec = layout_spec
        self.layoutdir = layoutdir
        self.filename = filename
        self.checkskip = checkskip
        self.layout = layout

    def abspath(self):
        return os.path.join(self.layoutdir, self.filename)

    def exists(self):
        return self.checkskip or os.path.exists(self.abspath)

    def absspec(self):
        if ":" in self.filename:
            return self.filename
        return os.path.join(self.layout_spec, self.filename)

@implementer(ILayoutModelResolver)
class LayoutModelDescriptorFactory(object):
    DescriptorBase = LayoutModelDescriptor
    DescriptorDefault = LayoutModelDescriptor
    def __init__(self, layout_spec, default_prefix="default", checkskip=False):
        self.layout_spec = layout_spec
        resolved = AssetResolver().resolve(layout_spec)
        if not resolved.exists():
            os.mkdir(resolved.abspath())
        self.layoutdir = resolved.abspath()
        self.default_prefix = default_prefix
        self.checkskip = checkskip

    def _resolve(self, request, layout, verbose=False):
        return self.from_layout(request, layout)        

    def resolve(self, request, layout, verbose=False):
        descriptor = self.from_layout(request, layout)
        if descriptor.exists():
            return descriptor
        if verbose:
            logger.info("layout template file %s is not found. lookup in default template path" % descriptor.abspath)

        descriptor = self.from_layout_default(request, layout)
        if verbose:
            logger.info("default template path %s is" % descriptor.abspath())
        return descriptor

    def from_layout_default(self, request, layout):
        filename_default = os.path.join(self.default_prefix, layout.template_filename)
        logger.info("layout template is not found. search %s" % (filename_default))
        return self.DescriptorDefault(
            self.layout_spec, 
            self.layoutdir, 
            filename_default, 
            checkskip=False, 
            layout=layout
            )
        
        return filename_default

    def from_layout(self, request, layout):
        return self.DescriptorBase(
            self.layout_spec, 
            self.layoutdir, 
            layout.prefixed_template_filename, 
            checkskip=self.checkskip, 
            layout=layout
            )
