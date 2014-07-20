# encoding: utf-8

from altair.metadata import DefaultModelAttributeMetadataProvider

metadata_provider = DefaultModelAttributeMetadataProvider(
    'booster.89ers',
    {
        'extra.mail_permission': {
            'display_name': {
                'ja_JP': u'メールマガジン',
                },
            'type': bool,
            'coercer': lambda x: bool(int(x)) if isinstance(x, int) else x,
            },
        'extra.publicity': {
            'display_name': {
                'ja_JP': u'メモリアルブックへの氏名掲載希望',
                },
            'type': unicode,
            },
        'extra.t_shirts_size': {
            'display_name': {
                'ja_JP': u'Ｔシャツサイズ',
                },
            'type': unicode,
            },
        'extra.official_ball': {
            'display_name': {
                'ja_JP': u'オリジナル公式球への記載希望',
                },
            'type': unicode,
            },
        'extra.coupon': {
            'display_name': {
                'ja_JP': u'特典の会場受け取り希望',
                },
            'type': unicode,
            },
        'extra.motivation': {
            'display_name': {
                'ja_JP': u'クラブナイナーズに入会しようと思ったきっかけ',
                },
            'type': unicode,
            },
        'extra.num_times_at_venue': {
            'display_name': {
                'ja_JP': u'昨シーズンの会場での観戦回数',
                },
            'type': int,
            'coercer': lambda x: int(x) if x else 0,
            },
        }
    )
        
