# -*- coding: utf-8 -*-

from collections import OrderedDict

import helpers

from paste.util.multidict import MultiDict
from sqlalchemy.sql.expression import or_

from altair.app.ticketing.mailmags.models import MailSubscription, MailMagazine, MailSubscriptionStatus
from altair.app.ticketing.utils import dereference
from altair.app.ticketing.csvutils import CSVRenderer, PlainTextRenderer, CollectionRenderer, AttributeRenderer, SimpleRenderer

def one_or_empty(b):
    return u'1' if b else u''

japanese_columns = {
    u'email': u'メールアドレス',
    u'status': u'状態',
    u'created_at': u'登録日時',
    u'updated_at': u'データ更新日時',
    }

def get_japanese_columns(request):
    return dict(japanese_columns)

class MailMagCSV(object):
    column_renderers = [
        PlainTextRenderer(u'email'),
        PlainTextRenderer(u'status'),
        PlainTextRenderer(u'created_at'),
        PlainTextRenderer(u'updated_at')
        ]

    def __init__(self, organization_id=None, localized_columns={}, excel_csv=False):
        column_renderers = None
        self.organization_id = organization_id
        self.localized_columns = localized_columns

    def __call__(self, mail_subscriptions):
        renderer = CSVRenderer(self.column_renderers, self)
        return renderer(
            (
                {
                    u'email':mail_subscription.email,
                    u'status':helpers.subscription_status(mail_subscription.status) or u'-',
                    u'created_at':mail_subscription.created_at,
                    u'updated_at':mail_subscription.updated_at
                    }
                for mail_subscription in mail_subscriptions
                ),
            localized_columns=self.localized_columns
            )
