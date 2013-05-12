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
    def __init__(self, layout_spec, layoutdir, filename, checkskip=False, layout=None, path_name_encoder=None):
        self.layout_spec = layout_spec
        self.layoutdir = layoutdir
        self.filename = filename
        self.checkskip = checkskip
        self.layout = layout
        self.path_name_encoder = path_name_encoder or (lambda path: path)

    def abspath(self):
        return os.path.join(
            self.path_name_encoder(self.layoutdir),
            self.path_name_encoder(self.filename))

    def exists(self):
        return self.checkskip or os.path.exists(self.abspath())

    def absspec(self):
        if ":" in self.filename:
            return self.path_name_encoder(self.filename)
        path = os.path.join(
            self.path_name_encoder(self.layout_spec),
            self.path_name_encoder(self.filename))
        module, path = path.split(":")
        return "{0}:{1}".format(module, os.path.normpath(path))
        

@implementer(ILayoutModelResolver)
class LayoutModelResolver(object):
    DescriptorBase = LayoutModelDescriptor
    DescriptorDefault = LayoutModelDescriptor
    def __init__(self, layout_spec, default_prefix="default", checkskip=False, fs_encoding='utf-8'):
        self.layout_spec = layout_spec
        resolved = AssetResolver().resolve(layout_spec)
        if not resolved.exists():
            os.makedirs(resolved.abspath())
        self.layoutdir = resolved.abspath()
        self.default_prefix = default_prefix
        self.checkskip = checkskip
        self.fs_encoding = fs_encoding

    def _encode_path_name(self, unistr_or_str):
        if isinstance(unistr_or_str, unicode):
            return unistr_or_str.encode(self.fs_encoding)
        else:
            return str(unistr_or_str)

    def _resolve(self, request, assetspec, verbose=False):
        return self.from_assetspec(request, assetspec)        

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

    def from_assetspec(self, request, filepath, layout=None):
        logger.info("layout template is not found. search %s" % (filepath))
        return self.DescriptorDefault(
            self.layout_spec, 
            self.layoutdir, 
            filepath, 
            checkskip=False, 
            layout=layout,
            path_name_encoder=self._encode_path_name
            )

    def from_layout_default(self, request, layout):
        filename_default = os.path.join(self.default_prefix, layout.template_filename)
        return self.from_assetspec(request, filename_default, layout)

    def from_layout(self, request, layout):
        return self.DescriptorBase(
            self.layout_spec, 
            self.layoutdir, 
            layout.prefixed_template_filename, 
            checkskip=self.checkskip, 
            layout=layout,
            path_name_encoder=self._encode_path_name
            )
