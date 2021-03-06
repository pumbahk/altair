import re
import sys
import logging
import json

from zope.interface import implementer
from zope.deprecation import deprecate
from altair.pyramid_boto.s3.assets import IS3KeyProvider
from altair.pyramid_assets import get_resolver
from altair.app.ticketing.utils import myurljoin
from .interfaces import IVenueSiteDrawingProvider, IVenueSiteDrawingProviderAdapterFactory
from .utils import is_drawing_compressed, get_s3_url

logger = logging.getLogger(__name__)

@implementer(IVenueSiteDrawingProvider)
class VenueSiteDrawingProviderAdapter(object):
    @property
    def _absolute_frontend_metadata_url(self):
        if self.site._frontend_metadata_url:
            return myurljoin(self._frontend_metadata_base_url, self.site._frontend_metadata_url)
        else:
            return None

    @property
    def _absolute_backend_metadata_url(self):
        if self.site._backend_metadata_url:
            return myurljoin(self._backend_metadata_base_url, self.site._backend_metadata_url)
        else:
            return None

    @property
    def frontend_metadata(self):
        frontend_metadata = self._frontend_metadata
        if not frontend_metadata and self._absolute_frontend_metadata_url is not None:
            resolver = get_resolver(self.request.registry)
            try:
                frontend_metadata = json.load(resolver.resolve(self._absolute_frontend_metadata_url).stream())
                self._frontend_metadata = frontend_metadata
            except:
                logger.error('failed to fetch frontend metadata from %s' % self._absolute_frontend_metadata_url, exc_info=sys.exc_info())
        return frontend_metadata

    @property
    def backend_metadata(self):
        backend_metadata = self._backend_metadata
        if not backend_metadata and self._absolute_backend_metadata_url is not None:
            resolver = get_resolver(self.request.registry)
            try:
                backend_metadata = json.load(resolver.resolve(self._absolute_backend_metadata_url).stream())
                self._backend_metadata = backend_metadata
            except:
                logger.error('failed to fetch backend metadata from %s' % self._absolute_frontend_metadata_url, exc_info=sys.exc_info())
        return backend_metadata

    def get_frontend_pages(self):
        return self.frontend_metadata and self.frontend_metadata.get('pages')

    def get_frontend_drawing(self, name):
        try:
            page_meta = self.get_frontend_pages().get(name)
        except:
            page_meta = None
        if page_meta is not None:
            resolver = get_resolver(self.request.registry)
            return resolver.resolve(myurljoin(self._absolute_frontend_metadata_url, name))
        else:
            return None

    def get_frontend_drawings(self):
        page_metas = self.get_frontend_pages()
        if page_metas is not None:
            resolver = get_resolver(self.request.registry)
            return dict((name, resolver.resolve(myurljoin(self._absolute_frontend_metadata_url, name))) for name in page_metas)
        else:
            return None

    def get_frontend_spa(self):
        return self.frontend_metadata and self.frontend_metadata.get('spa')

    def get_frontend_drawings_spa(self):
        spa_metas = self.get_frontend_spa()
        retval = {}
        if spa_metas is not None:
            resolver = get_resolver(self.request.registry)
            for name in spa_metas:
                map_tag = spa_metas.get(name)
                if 'root' in map_tag :
                    map_prefix = 'root'
                elif 'mini' in map_tag :
                    map_prefix = 'mini'
                elif 'seats' in map_tag :
                    map_prefix = 'seat'
                elif 'seat-groups' in map_tag :
                    map_prefix = 'seat-group'
                retval[map_prefix] = resolver.resolve(myurljoin(self._absolute_frontend_metadata_url, name))
            return dict(retval)
        else:
            return None

    def get_backend_pages(self):
        return self.backend_metadata and self.backend_metadata.get('pages') or dict(root=dict())

    def get_backend_drawing(self, name):
        try:
            page_meta = self.get_backend_pages().get(name)
        except:
            page_meta = None
        if page_meta is not None:
            resolver = get_resolver(self.request.registry)
            return resolver.resolve(myurljoin(self._absolute_backend_metadata_url, name))
        else:
            return None

    def get_backend_drawings(self):
        page_metas = self.get_backend_pages()
        resolver = get_resolver(self.request.registry)
        return dict((name, resolver.resolve(myurljoin(self._absolute_backend_metadata_url, name))) for name in page_metas)

    @property
    @deprecate(u'switch to get_backend_drawings')
    def drawing_url(self):
        drawing = self.get_backend_drawing('root.svg')
        if drawing is None:
            return self.site._drawing_url
        else:
            return drawing.path

    @property
    @deprecate(u'switch to get_backend_drawings')
    def direct_drawing_url(self):
        retval = self._direct_drawing_url
        if retval is None:
            drawing = self.get_backend_drawing('root.svg')
            if self._force_indirect_serving or drawing is None:
                retval = self.request.route_url('api.get_site_drawing', site_id=self.site.id)
            else:
                if IS3KeyProvider.providedBy(drawing):
                    retval = get_s3_url(drawing)
                else:
                    retval = self.request.static_url(drawing.path)
            self._direct_drawing_url = retval
        return retval

    def __init__(self, request, site, frontend_metadata_base_url, backend_metadata_base_url, force_indirect_serving):
        self._direct_drawing_url = None
        self.request = request
        self.site = site
        self._frontend_metadata_base_url = frontend_metadata_base_url
        self._backend_metadata_base_url = backend_metadata_base_url
        self._force_indirect_serving = force_indirect_serving
        self._frontend_metadata = None
        self._backend_metadata = None

@implementer(IVenueSiteDrawingProviderAdapterFactory)
class VenueSiteDrawingProviderAdapterFactory(object):
    def __init__(self, frontend_metadata_base_url, backend_metadata_base_url, force_indirect_serving):
        self.frontend_metadata_base_url = frontend_metadata_base_url
        self.backend_metadata_base_url = backend_metadata_base_url
        self.force_indirect_serving = force_indirect_serving

    def __call__(self, request, site):
        return VenueSiteDrawingProviderAdapter(request, site, self.frontend_metadata_base_url, self.backend_metadata_base_url, self.force_indirect_serving)
