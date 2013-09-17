# -*- coding:utf-8 -*-
from altair.metadata import DefaultModelAttributeMetadataProvider
from altair.app.ticketing.core.models import PaymentMethod

METADATA_NAME_ORDERED_PRODUCT = "OrderedProduct"
METADATA_NAME_ORDER = "Order"


order_metadata_provider = DefaultModelAttributeMetadataProvider(
    "ticketing.admin", 
    {
        'sales_counter_payment_method_id': {
            'display_name': {
                'ja_JP': u"当日窓口決済"
            }, 
            'coercer': lambda id: PaymentMethod.query.get(id).name if id else None
        }, 
        'memo_on_order1': {
            'display_name': {
                'ja_JP': u"予約時補助文言1"
            }
        }, 
        'memo_on_order2': {
            'display_name': {
                'ja_JP': u"予約時補助文言2"
            }
        }, 
        'memo_on_order3': {
            'display_name': {
                'ja_JP': u"予約時補助文言3"
            }
        }, 
    }
)
