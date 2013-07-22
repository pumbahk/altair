# encoding: utf-8

from altair.app.ticketing.orders.metadata import DefaultOrderedProductAttributeMetadataProvider

metadata_provider = DefaultOrderedProductAttributeMetadataProvider(
    'booster.bambitious',
    {
        'product_delivery_method_name': {
            'display_name': {
                'ja_JP': u'会員特典受取方法',
                },
            'type': unicode,
            }
        }
    )
        

