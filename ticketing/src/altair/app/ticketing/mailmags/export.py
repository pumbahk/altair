# -*- coding: utf-8 -*-

from collections import OrderedDict

import helpers

from paste.util.multidict import MultiDict
from sqlalchemy.sql.expression import or_

from altair.app.ticketing.mailmags.models import MailSubscription, MailMagazine, MailSubscriptionStatus
from altair.app.ticketing.utils import dereference
from altair.app.ticketing.csvutils import CSVRenderer, PlainTextRenderer, CollectionRenderer, AttributeRenderer, SimpleRenderer
from altair.app.ticketing.orders.api import get_metadata_provider_registry

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
            if isinstance(column_renderer, PlainTextRenderer) and column_renderer.fancy and not excel_csv:
                column_renderer = PlainTextRenderer(
                    column_renderer.key,
                    column_renderer.name,
                    column_renderer.empty_if_dereference_fails
                    )
            return column_renderer

        self.column_renderers = map(bind, column_renderers)
        self.organization_id = organization_id
        self.localized_columns = localized_columns

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
