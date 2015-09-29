# encoding: utf-8

import logging
from pyramid.decorator import reify
from altair.mobile.interfaces import IMobileRequest, ISmartphoneRequest
from altair.app.ticketing.mails.interfaces import IMailRequest
from altair.app.ticketing.cart import api as cart_api

logger = logging.getLogger(__name__)

def get_coupon_view_context_factory(default_package):
    if not isinstance(default_package, basestring):
        default_package = default_package.__name__

    class OrderReviewViewContext(object):
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
            organization_short_name = None
            try:
                organization_short_name = self.request.organization.short_name
            except Exception as e:
                logger.warn('organization_short_name not found (%s)' % e.message)
            return organization_short_name

        @property
        def cart_setting(self):
            if self.context is not None and hasattr(self.context, 'cart_setting'):
                return self.context.cart_setting
            else:
                # falls back to the default
                return self.request.organization.setting.cart_setting

        @property
        def title(self):
            return u'申込履歴確認'

        @property
        def contact_url(self):
            return self.cart_setting.contact_url or cart_api.safe_get_contact_url(self.request)

        @property
        def contact_url_mobile(self):
            return self.cart_setting.contact_url_mobile or cart_api.safe_get_contact_url(self.request)

        @property
        def team_name(self):
            return self.request.organization.name

        @property
        def extra_footer_links(self):
            return self.cart_setting.extra_footer_links or []

        @property
        def extra_footer_links_mobile(self):
            return self.cart_setting.extra_footer_links_mobile or []

        def get_template_path(self, path):
            organization_short_name = self.organization_short_name or "__default__"
            package_or_path, colon, _path = path.partition(':')
            if not colon:
                package = default_package
                path = package_or_path
            else:
                package = package_or_path
                path = _path
            return '%(package)s:templates/%(organization_short_name)s/%(ua_type)s/%(path)s' % dict(
                package=package,
                organization_short_name=organization_short_name,
                ua_type=self.ua_type,
                path=path)

        def static_url(self, path, *args, **kwargs):
            return self.request.static_url("altair.app.ticketing.orderreview:static/%(organization_short_name)s/%(path)s" % dict(organization_short_name=self.organization_short_name, path=path), *args, **kwargs)

        def __getattr__(self, k):
            return getattr(self.cart_setting, k)
    return OrderReviewViewContext

def includeme(config):
    config.add_request_method(get_coupon_view_context_factory(config.registry), 'view_context', reify=True)
