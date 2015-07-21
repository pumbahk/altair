# encoding: utf-8

from pyramid.decorator import reify
from altair.mobile.interfaces import IMobileRequest, ISmartphoneRequest
from altair.app.ticketing.mails.api import get_sender_address
from altair.app.ticketing.core.models import MailTypeEnum
from altair.app.ticketing.mails.interfaces import IMailRequest
from . import api
from .interfaces import ICartResource
from .resources import PerformanceOrientedTicketingCartResource
from .exceptions import CartException

import logging

logger = logging.getLogger(__name__)

def get_cart_view_context_factory(default_package):
    if not isinstance(default_package, basestring):
        default_package = default_package.__name__

    class CartViewContext(object):
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
                if IMailRequest.providedBy(self.request):
                    membership = self.context.membership
                    if membership is None:
                        logger.warning('membership is None for context %r' % self.context)
                        return None
                    else:
                        return membership.name
                else:
                    membership_name = self.request.altair_auth_info['membership']
                    if membership_name is not None:
                        return membership_name
                    matchdict = getattr(self.request, 'matchdict', None)
                    if matchdict is None:
                        return None
                    return matchdict.get('membership')
            except:
                logger.exception('WTF?')

        @reify
        def organization_short_name(self):
            organization_short_name = None
            try:
                organization_short_name = api.get_organization(self.request).short_name
            except Exception as e:
                logger.warn('organization_short_name not found (%s)' % e.message)
            return organization_short_name

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
        def title(self):
            if self.cart_setting.title:
                return self.cart_setting.title
            else:
                return self.context.event.title

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
            return api.get_organization(self.request).name

        @reify
        def mail_filter_domain_notice(self):
            template = u'※ 注文受付完了、確認メール等をメールでご案内します。「{domain}」からのメールを受信できるよう、お申し込み前にドメイン指定の設定を必ずお願いいたします。'
            if self.cart_setting and self.cart_setting.mail_filter_domain_notice_template:
                template = self.cart_setting.mail_filter_domain_notice_template

            try:
                if hasattr(self.context, 'performance'):
                    sender = get_sender_address(self.request, performance=self.context.performance, mail_type=MailTypeEnum.PurchaseCompleteMail.v)
                elif hasattr(self.context, 'lot'):
                    sender = get_sender_address(self.request, lot=self.context.lot, mail_type=MailTypeEnum.LotsAcceptedMail.v)
                elif hasattr(self.context, 'event'):
                    sender = get_sender_address(self.request, event=self.context.event, mail_type=MailTypeEnum.PurchaseCompleteMail.v)
                elif hasattr(self.context, 'organization'):
                    sender = get_sender_address(self.request, organization=self.context.organization, mail_type=MailTypeEnum.PurchaseCompleteMail.v)
                else:
                    raise NotImplemented("context must have any one of the following attributes: performance, event and organization")
                _, _, domain = sender.partition('@')
                return template.format(domain=domain)
            except:
                logger.exception('oops')
                raise

        def get_template_path(self, path):
            organization_short_name = self.organization_short_name or "__default__"
            membership = self.membership or "__default__"
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
                membership=membership,
                ua_type=self.ua_type,
                path=path)

        def static_url(self, path, *args, **kwargs):
            return self.request.static_url("altair.app.ticketing.cart:static/%(organization_short_name)s/%(path)s" % dict(organization_short_name=self.organization_short_name, path=path), *args, **kwargs)

        def __getattr__(self, k):
            return getattr(self.cart_setting, k)

    return CartViewContext

def determine_layout(event):
    request = event.request
    if ICartResource.providedBy(request.context):
        try:
            cart_setting = request.context.cart_setting
        except CartException:
            cart_setting = request.organization.setting.cart_setting
        if api.is_booster_cart(cart_setting):
            request.layout_manager.use_layout('booster')
        elif api.is_fc_cart(cart_setting):
            request.layout_manager.use_layout('fc')

def includeme(config):
    config.add_request_method(get_cart_view_context_factory(config.registry), 'view_context', reify=True)
    config.add_subscriber(determine_layout, 'pyramid.events.ContextFound')
