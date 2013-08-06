# -*- coding: utf-8 -*-

from collections import OrderedDict

import helpers

from paste.util.multidict import MultiDict
from sqlalchemy.sql.expression import or_

from altair.app.ticketing.cart.helpers import format_number as _format_number
from altair.app.ticketing.mailmags.models import MailSubscription, MailMagazine, MailSubscriptionStatus
from altair.app.ticketing.utils import dereference
from altair.app.ticketing.csvutils import CSVRenderer, PlainTextRenderer, CollectionRenderer, AttributeRenderer, SimpleRenderer
from altair.app.ticketing.orders.api import get_metadata_provider_registry

def format_number(value):
    return _format_number(float(value))

def _create_mailsubscription_cache(organization_id):
    D = dict()
    query = MailSubscription.query\
        .filter(MailSubscription.segment_id == MailMagazine.id)\
        .filter(or_(MailSubscription.status == None, MailSubscription.status == MailSubscriptionStatus.Subscribed.v))
    if organization_id:
        query = query.filter(MailMagazine.organization_id == organization_id)
    for ms in query:
        D[ms.email] = True
    return D

def one_or_empty(b):
    return u'1' if b else u''

japanese_columns = {
    u'email': u'メールアドレス',
    u'status': u'状態',
    u'created_at': u'登録日時',
    u'updated_at': u'データ更新日時',
    }

def get_japanese_columns(request):
    retval = dict(japanese_columns)
    registry = get_metadata_provider_registry(request)
    for provider in registry.getProviders():
        for key in provider:
            metadata = provider[key]
            retval[u'attribute[%s]' % metadata.key] = metadata.get_display_name('ja_JP')
    return retval

class MarginRenderer(object):
    def __init__(self, key, column_name):
        self.key = key
        self.column_name = column_name

    def __call__(self, record):
        order = dereference(record, self.key)
        rendered_value = 0
        for ordered_product in order.ordered_products:
            margin = (ordered_product.product.sales_segment.margin_ratio / 100) if ordered_product.product.sales_segment is not None else 0
            rendered_value += (ordered_product.price * ordered_product.quantity) * margin
        return [
            ((u"", self.column_name, u""), unicode(rendered_value))
        ]

class PerSeatQuantityRenderer(object):
    def __init__(self, key, column_name):
        self.key = key
        self.column_name = column_name

    def __call__(self, record):
        ordered_product_item = dereference(record, self.key)
        if ordered_product_item.seats:
            rendered_value = u"1"
        else:
            rendered_value = unicode(ordered_product_item.quantity)
        return [
            (
                (u"", self.column_name, u""),
                rendered_value
                )
            ]

class MailMagazineSubscriptionStateRenderer(object):
    def __init__(self, key, column_name):
        self.key = key
        self.column_name = column_name
        self.outer = None

    def __call__(self, record):
        assert self.outer is not None
        emails = dereference(record, self.key, True) or []
        return [
            (
                (u"", self.column_name, u""),
                one_or_empty(any(self.outer.mailsubscription_cache.get(email, False) for email in emails))
                )
            ]

class CurrencyRenderer(SimpleRenderer):
    def __call__(self, record):
        return [
            ((u'', self.name, u''), unicode(format_number(dereference(record, self.key))))
            ]

class ZipRenderer(SimpleRenderer):
    def __call__(self, record):
        zip = dereference(record, self.key, True)
        zip = ('%s-%s' % (zip[0:3], zip[3:])) if zip else ''
        return [
            ((u'', self.name, u''), zip)
        ]

class PrintHistoryRenderer(object):
    def __init__(self, key, column_name):
        self.key = key
        self.column_name = column_name

    def __call__(self, record):
        ordered_product_item = dereference(record, self.key)
        return [
            (
                (u"", self.column_name, u""),
                u", ".join(list(OrderedDict([(print_history.operator.name, True) for print_history in ordered_product_item.print_histories if print_history.operator is not None])))
                )
            ]

class MailMagCSV(object):
    EXPORT_TYPE_MAILMAG = 1

    common_columns_pre = [
        PlainTextRenderer(u'email'),
        PlainTextRenderer(u'status'),
        PlainTextRenderer(u'created_at'),
        PlainTextRenderer(u'updated_at')]

    per_mailmag_columns = common_columns_pre

    def __init__(self, export_type=EXPORT_TYPE_MAILMAG, organization_id=None, localized_columns={}, excel_csv=False):
        self.export_type = export_type
        column_renderers = None
        if export_type == self.EXPORT_TYPE_MAILMAG:
            column_renderers = self.per_mailmag_columns
        if column_renderers is None:
            raise ValueError('export_type')

        def bind(column_renderer):
            if isinstance(column_renderer, MailMagazineSubscriptionStateRenderer):
                column_renderer = MailMagazineSubscriptionStateRenderer(column_renderer.key, column_renderer.column_name)
                column_renderer.outer = self
            elif isinstance(column_renderer, PlainTextRenderer) and column_renderer.fancy and not excel_csv:
                column_renderer = PlainTextRenderer(
                    column_renderer.key,
                    column_renderer.name,
                    column_renderer.empty_if_dereference_fails
                    )
            return column_renderer

        self.column_renderers = map(bind, column_renderers)
        self.organization_id = organization_id
        self._mailsubscription_cache = None
        self.localized_columns = localized_columns

    @property
    def mailsubscription_cache(self):
        if self._mailsubscription_cache is None:
            self._mailsubscription_cache = _create_mailsubscription_cache(self.organization_id)
        return self._mailsubscription_cache

    def iter_records(self, mail_subscription):
        common_record = {
            u'email':mail_subscription.email,
            u'status':helpers.subscription_status(mail_subscription.status) or u'-',
            u'created_at':mail_subscription.created_at,
            u'updated_at':mail_subscription.updated_at
            }
        if self.export_type == self.EXPORT_TYPE_MAILMAG:
            record = dict(common_record)
            yield record
        else:
            raise ValueError(self.export_type)

    def __call__(self, mail_subscriptions):
        renderer = CSVRenderer(self.column_renderers)
        for mail_subscription in mail_subscriptions:
            for record in self.iter_records(mail_subscription):
                renderer.append(record)
        return renderer(localized_columns=self.localized_columns)
