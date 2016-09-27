# encoding: utf-8

import logging
import os
from pyramid.decorator import reify
from pyramid.path import AssetResolver
from altair.mobile.interfaces import IMobileRequest, ISmartphoneRequest
from altair.app.ticketing.mails.interfaces import IMailRequest
from altair.app.ticketing.cart import api as cart_api

logger = logging.getLogger(__name__)

def get_orderreview_view_context_factory(default_package):
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
        def membership(self):
            try:
                return self.request.altair_auth_info['membership'] or self.request.matchdict.get('membership')
            except:
                logger.exception('WTF?')

        @reify
        def organization_short_name(self):
            organization_short_name = None
            try:
                organization_short_name = self.request.organization.short_name
            except Exception as e:
                logger.warn('organization_short_name not found (%s)' % e.message)
            return organization_short_name

        @reify
        def organization_contact_email(self):
            organization_contact_email = None
            try:
                organization_contact_email = self.request.organization.contact_email
            except Exception as e:
                logger.warn('organization_contact_email not found (%s)' % e.message)
            return organization_contact_email

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

        def get_fc_login_template(self, package=None, template_name='login.html'):
            organization_short_name = self.organization_short_name or "__default__"
            if package is None:
                package = default_package

            # __scaffold__シムリンクのORGのfc_authテンプレート
            # こちらの方を優先
            template_path = '{package}:templates/{organization_short_name}/fc_auth/{ua_type}/{template_name}'\
                .format(package=package,
                organization_short_name=organization_short_name,
                ua_type=self.ua_type,
                template_name=template_name)

            # 存在確認
            assetresolver = AssetResolver()
            physical_path = assetresolver.resolve(template_path).abspath()
            if os.path.exists(physical_path):
                return template_path

            # scaffoldシムリンク系のORGでない場合
            # 従来のORG設定で作成していたfc_authテンプレートを確認
            template_path = '{package}:templates/{organization_short_name}/{ua_type}/fc_auth/{template_name}'\
                .format(package=package,
                organization_short_name=organization_short_name,
                ua_type=self.ua_type,
                template_name=template_name)

            # 存在確認
            physical_path = assetresolver.resolve(template_path).abspath()
            if os.path.exists(physical_path):
                return template_path
            else:
                return None

        def static_url(self, path, module=None, *args, **kwargs):
            if module is None:
                module='orderreview'
            return self.request.static_url("altair.app.ticketing.%(module)s:static/%(organization_short_name)s/%(path)s" % dict(organization_short_name=self.organization_short_name, path=path, module=module), *args, **kwargs)

        def __getattr__(self, k):
            return getattr(self.cart_setting, k)
    return OrderReviewViewContext

def includeme(config):
    config.add_request_method(get_orderreview_view_context_factory(config.registry), 'view_context', reify=True)
