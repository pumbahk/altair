# encoding: utf-8

from ticketing.orders.metadata import DefaultOrderedProductAttributeMetadataProvider

metadata_provider = DefaultOrderedProductAttributeMetadataProvider(
    'booster.bigbulls',
    {
        'extra.mail_permission': {
            'display_name': {
                'ja_JP': u'メールマガジン',
                },
            'type': bool,
            'coercer': lambda x: bool(int(x)),
            },
        'extra.publicity': {
            'display_name': {
                'ja_JP': u'ゲームプログラムへのお名前掲載',
                },
            'type': bool,
            'coercer': lambda x: (x == 'yes' if x is not None else None),
            },
        'extra.t_shirts_size': {
            'display_name': {
                'ja_JP': u'Tシャツサイズ',
                },
            'type': unicode,
            },
        'extra.replica_uniform_size': {
            'display_name': {
                'ja_JP': u'レプリカユニフォームサイズ',
                },
            'type': unicode,
            },
        'extra.authentic_uniform_size': {
            'display_name': {
                'ja_JP': u'オーセンティックユニフォームサイズ',
                },
            'type': unicode,
            },
        'extra.authentic_uniform_no': {
            'display_name': {
                'ja_JP': u'オーセンティックユニフォーム背番号',
                },
            'type': unicode,
            },
        'extra.authentic_uniform_name': {
            'display_name': {
                'ja_JP': u'オーセンティックユニフォーム名前',
                },
            'type': unicode,
            },
        'extra.authentic_uniform_color': {
            'display_name': {
                'ja_JP': u'オーセンティックユニフォーム色',
                },
            'type': unicode,
            'coercer': (lambda x: {"red": u"赤", "white": u"白"}.get(x)), 
            },
        'extra.parent_first_name': {
            'display_name': {
                'ja_JP': u'保護者名',
                },
            'type': unicode,
            },
        'extra.parent_last_name': {
            'display_name': {
                'ja_JP': u'保護者姓',
                },
            'type': unicode,
            },
        'extra.parent_first_name_kana': {
            'display_name': {
                'ja_JP': u'保護者メイ',
                },
            'type': unicode,
            },
        'extra.parent_last_name_kana': {
            'display_name': {
                'ja_JP': u'保護者セイ',
                },
            'type': unicode,
            },
        'extra.relationship': {
            'display_name': {
                'ja_JP': u'続柄',
                },
            'type': unicode,
            },
        })
        
