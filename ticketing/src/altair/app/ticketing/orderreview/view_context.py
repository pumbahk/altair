# encoding: utf-8

import logging
import os
from pyramid.decorator import reify
from pyramid.path import AssetResolver
from altair.mobile.interfaces import IMobileRequest, ISmartphoneRequest
from altair.app.ticketing.core.utils import (search_template_file,
                                             search_static_file)
from altair.app.ticketing.mails.interfaces import IMailRequest
from altair.app.ticketing.cart import api as cart_api

logger = logging.getLogger(__name__)

def get_orderreview_view_context_factory(default_package):
    if not isinstance(default_package, basestring):
        default_package = default_package.__name__

    class OrderReviewViewContext(object):
        def __init__(self, request):
            self.request = request
            self.context = getattr(request, 'context', None)  # will not be available for exception views
            self.default_package = default_package

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

        @property
        def membership_login_body(self):
            return None

        def get_template_path(self, path):
            override_path_str = None
            if self.ua_type == 'smartphone':  # order_reviewのテンプレートはスマホもPCテンプレートで対応
                override_path_str = u'{package}:templates/{organization_short_name}/pc/{path}'

            return search_template_file(self, path, default_package, override_path_str)

        def get_fc_login_template(self, package=None, template_name='login.html'):
            path = template_name

            # 第2参照テンプレートが__base__になっている場合はモジュールのfc_authを参照するようにする。
            # cartやorderreview配下のfc_authディレクトリは参照しない。
            if self.request.organization.setting.rendered_template_2 == '__base__':
                override_path_str = u'altair.app.ticketing.fc_auth:templates/{organization_short_name}/{ua_type}/{path}'
                return search_template_file(self, path, package, override_path_str)

            # ORGによってfc_authと{ua_type}のディレクトリの順番が逆になっているものがあるため、2回テンプレートのパスを確認
            if package is None:
                package = default_package

            override_path_str = u'{package}:templates/{organization_short_name}/fc_auth/{ua_type}/{path}'
            first_try = search_template_file(self, path, package, override_path_str)
            if first_try is not None:
                return first_try

            override_path_str = u'{package}:templates/{organization_short_name}/{ua_type}/fc_auth/{path}'
            second_try = search_template_file(self, path, package, override_path_str)
            return second_try

        def get_include_template_path(self, path):
            override_path_str = u'{package}:templates/{organization_short_name}/includes/{path}'
            return search_template_file(self, path, default_package, override_path_str)

        def static_url(self, path, module=None, **kwargs):
            if module is None:
                module = 'orderreview'

            static_path = search_static_file(self, path, module)
            url = self.request.static_url(static_path, **kwargs)

            # TKT-5968 self.request.script_nameである"orderreview/"が強制的に付加されてしまうため、かき消し
            # (mypage機能がorderreviewモジュール内に含まれているため）
            if (module == 'fc_auth') and ('orderreview/' in url):
                url = url.replace('orderreview/', '')

            return url

        def __getattr__(self, k):
            return getattr(self.cart_setting, k)

    return OrderReviewViewContext


def includeme(config):
    config.add_request_method(get_orderreview_view_context_factory(config.registry), 'view_context', reify=True)
