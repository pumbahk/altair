# encoding: utf-8

from altair.app.ticketing.orders.metadata import DefaultOrderedProductAttributeMetadataProvider

metadata_provider = DefaultOrderedProductAttributeMetadataProvider(
    'booster',
    {
        'cont': {
            'display_name': {
                'ja_JP': u'区分 (継続=yes)',
                },
            'type': bool,
            'coercer': lambda x: x == 'yes' if x is not None else False,
            },
        'old_id_number': {
            'display_name': {
                'ja_JP': u'昨年度会員番号',
                },
            'type': unicode,
            },
        'member_type': {
            'display_name': {
                'ja_JP': u'会員種別',
                },
            'type': unicode,
            },
        't_shirts_size': {
            'display_name': {
                'ja_JP': u'ブースターシャツサイズ',
                }
            },
        'year': {
            'display_name': {
                'ja_JP': u'誕生日 (年)',
                },
            'type': int,
            },
        'month': {
            'display_name': {
                'ja_JP': u'誕生日 (月)',
                },
            'type': int,
            },
        'day': {
            'display_name': {
                'ja_JP': u'誕生日 (日)',
                },
            'type': int,
            },
        'sex': {
            'display_name': {
                'ja_JP': u'性別',
                },
            'type': unicode,
            'coercer': (lambda x: {"male": u"男", "female": u"女"}.get(x, u"不明")), 
            },
        'fax': {
            'display_name': {
                'ja_JP': u'FAX番号',
                },
            'type': unicode,
            },
        }
    )
