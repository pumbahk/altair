# encoding: utf-8

from pyramid.decorator import reify
from altair.mobile.interfaces import IMobileRequest, ISmartphoneRequest
from altair.app.ticketing.mails.api import get_sender_address
from altair.app.ticketing.core.models import MailTypeEnum
from altair.app.ticketing.mails.interfaces import IMailRequest

import logging

logger = logging.getLogger(__name__)

STATIC_URL_PREFIX = '/static/'
CDN_URL_PREFIX = '/extauth/static/'
STATIC_ASSET_SPEC = '%(package)s:static/'

def get_view_context_factory(default_package):
    if not isinstance(default_package, basestring):
        default_package = default_package.__name__

    class ExtAuthViewContext(object):
        def __init__(self, request):
            self.request = request
            self.context = getattr(request, 'context', None) # will not be available for exception views

        @reify
        def ua_type(self):
            if IMailRequest.providedBy(self.request):
                ua_type = 'mail'
            elif IMobileRequest.providedBy(self.request):
                ua_type = 'mobile'
            elif ISmartphoneRequest.providedBy(self.request):
                ua_type = 'smartphone'
            else:
                ua_type = 'pc'
            return ua_type

        @reify
        def organization_short_name(self):
            return self.request.organization.short_name

        @property
        def cart_setting(self):
            if self.context is not None:
                try:
                    return self.context.cart_setting
                except AttributeError as err:
                    logger.warn('Failed to get the cart_setting: {}: {}'.format(self.context, err))
                    return None
            else:
                # falls back to the default
                return self.request.organization.setting.cart_setting

        @property
        def subtype(self):
            if self.context is not None:
                try:
                    return self.context.subtype
                except AttributeError as err:
                    logger.warn('Failed to get subtype: {}: {}'.format(self.context, err))
                    return None
            else:
                return None

        @property
        def orderreview_page_url(self):
            return self.cart_setting.orderreview_page_url or ('https://%s/orderreview' % self.request.host)

        @property
        def contact_url(self):
            return self.cart_setting.contact_url or api.safe_get_contact_url(self.request)

        @property
        def contact_url_mobile(self):
            return self.cart_setting.contact_url_mobile or api.safe_get_contact_url(self.request)

        @property
        def extra_footer_links(self):
            return self.cart_setting.extra_footer_links or []

        @property
        def extra_footer_links_mobile(self):
            return self.cart_setting.extra_footer_links_mobile or []

        @property
        def team_name(self):
            return self.request.organization.name

        def static_url(self, path, *args, **kwargs):
            return self.request.static_url(
                (STATIC_ASSET_SPEC + "/%(organization_short_name)s/%(path)s") % dict(
                    package=package,
                    organization_short_name=self.organization_short_name,
                    path=path
                    ),
                *args, **kwargs
                )

        def __getattr__(self, k):
            return getattr(self.cart_setting, k)

    return ExtAuthViewContext

def setup_static_views(config, package=None):
    if package is not None:
        package = config.registry.default_package.__name__

    settings = config.registry.settings
    config.include("altair.cdnpath")
    from altair.cdnpath import S3StaticPathFactory
    params = dict(package=package)
    config.add_cdn_static_path(S3StaticPathFactory(
        settings["s3.bucket_name"],
        exclude=config.maybe_dotted(settings.get("s3.static.exclude.function")),
        mapping={
            (STATIC_ASSET_SPEC % params): CDN_URL_PREFIX
            }
        ))
    config.add_static_view(STATIC_URL_PREFIX, STATIC_ASSET_SPEC % params, cache_max_age=3600)

def includeme(config):
    config.add_request_method(get_view_context_factory(config.registry), 'view_context', reify=True)
    setup_static_views(config)
