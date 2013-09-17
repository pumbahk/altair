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
            'coercer': lambda x: bool(int(x)),
            },
        'extra.publicity': {
            'display_name': {
                'ja_JP': u'メモリアルブックへの氏名掲載希望',
                },
            'type': bool,
            'coercer': lambda x: (x == 'yes' if x is not None else None),
            },
        'extra.motivation': {
            'display_name': {
                'ja_JP': u'ブースタークラブに入会しようと思ったきっかけ',
                },
            'type': unicode,
            },
        'extra.num_times_at_venue': {
            'display_name': {
                'ja_JP': u'昨シーズンの会場での観戦回数',
                },
            'type': int,
            'coercer': lambda x: int(x) if x is not None else 0,
            },
        }
    )
        
