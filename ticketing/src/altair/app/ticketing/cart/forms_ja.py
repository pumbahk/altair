# -*- coding:utf-8 -*-
from altair.formhelpers.translations import Translations
from altair.formhelpers.form import OurForm, OurDynamicForm
from wtforms.validators import Regexp, Length, Optional, EqualTo, AnyOf
from altair.formhelpers.validators import (
    Required,
    Phone,
    Zenkaku,
    Katakana,
    SejCompliantEmail,
    CP932,
    SwitchOptional,
    DynSwitchDisabled,
    )
from altair.formhelpers.fields.core import (
    OurTextField,
    OurRadioField,
    OurBooleanField,
    OurSelectField,
    OurIntegerField,
    OurFormField,
    )
from altair.formhelpers.fields.liaison import (
    Liaison,
    )
from altair.formhelpers.filters import (
    strip_spaces,
    ignore_space_hyphen,
    text_type_but_none_if_not_given,
    NFKC,
    lstrip,
    )
from .schemas import length_limit_for_sej

countries = [
    u'日本',
    u'アルジェリア', u'アンゴラ', u'アルメニア', u'アゼルバイジャン', u'オーストラリア', u'アルバニア', u'オーストリア', u'アングィラ', u'アンティグアバーブーダ', u'アルゼンチン',
    u'バーレーン', u'ベニン', u'ボツワナ', u'ブルキナファソ', u'ブータン', u'ブルネイ・ダルサラーム', u'ベラルーシ', u'ベルギー', u'ブルガリア', u'バハマ', u'バルバドス', u'ベリーズ', u'バミューダ', u'ボリビア', u'ブラジル',
    u'カーボベルデ', u'チャド', u'コンゴ共和国', u'カンボジア', u'中国', u'クロアチア', u'チェコ共和国', u'キプロス', u'ケイマン諸島', u'チリ', u'コロンビア', u'コスタリカ', u'カナダ',
    u'ドミニカ', u'ドミニカーナ',
    u'ドイツ',
    u'エジプト', u'エストニア', u'エクアドル', u'エルサルバドル',
    u'フィジー', u'フランス', u'フィンランド',
    u'ガンビア', u'ガーナ', u'ギニアビサウ', u'ギリシャ', u'グレナダ', u'グアテマラ', u'ガイアナ',
    u'香港', u'ハンガリー', u'ホンジュラス',
    u'インド', u'イスラエル', u'インドネシア', u'アイスランド', u'アイルランド', u'イタリア',
    u'ヨルダン', u'ジャマイカ',
    u'ケニア', u'クウェート', u'カザフスタン', u'韓国', u'キルギスタン',
    u'リベリア', u'ラオス', u'レバノン', u'ラトビア', u'リトアニア', u'ルクセンブルグ',
    u'マダガスカル', u'マラウイ', u'マリ', u'モーリタニア', u'モーリシャス', u'モザンビーク', u'マカオ', u'マレーシア', u'ミクロネシア連邦州', u'モンゴル', u'マケドニア', u'マルタ', u'モルドバ', u'メキシコ', u'モントセラト',
    u'ナミビア', u'ニジェール', u'ナイジェリア', u'ネパール', u'ニュージーランド', u'オランダ', u'ノルウェー', u'ニカラグア',
    u'オマーン', u'カタール',
    u'パキスタン', u'パラオ', u'パプアニューギニア', u'フィリピン', u'ポルスカ', u'ポルトガル', u'パナマ', u'パラグアイ', u'ペルー',
    u'ルーマニア', u'ロシア',
    u'サントメプリンシペ', u'サウジアラビア', u'セネガル', u'セイシェル', u'シエラレオネ', u'南アフリカ', u'スワジランド', u'シンガポール', u'ソロモン諸島', u'スリランカ', u'スペイン', u'スイス', u'スロバキア', u'スロベニア', u'スウェーデン', u'セントキッツ＆ネイビス', u'セントルシア', u'セントビンセント・グレナディーン', u'スリナム',
    u'タンザニア', u'チュニジア', u'台湾', u'タジキスタン', u'タイ', u'トルクメニスタン', u'トルコ', u'トリニダード＆トバゴ', u'タークス＆カイコス',
    u'ウガンダ', u'アラブ首長国連邦', u'ウズベキスタン', u'イギリス', u'ウルグアイ', u'米国',
    u'ベトナム', u'ベネズエラ', u'イギリス領バージン諸島',
    u'イエメン',
    u'ジンバブエ'
]

class ClientForm(OurDynamicForm):
    """国際化の日本語フォーム"""
    def _get_translations(self):
        return Translations()

    last_name = OurTextField(
        label=u"姓",
        note=u"(全角)",
        filters=[strip_spaces],
        validators=[
            Required(),
            Zenkaku,
            length_limit_for_sej,
            ],
        )
    last_name_kana = OurTextField(
        label=u"姓(カナ)",
        note=u"(全角カナ)",
        filters=[strip_spaces, NFKC],
        validators=[
            Required(),
            Katakana,
            length_limit_for_sej,
            ]
        )
    first_name = OurTextField(
        label=u"名",
        note=u"(全角)",
        filters=[strip_spaces],
        validators=[
            Required(),
            Zenkaku,
            length_limit_for_sej,
            ]
        )
    first_name_kana = OurTextField(
        label=u"名(カナ)",
        note=u"(全角カナ)",
        filters=[strip_spaces, NFKC],
        validators=[
            Required(),
            Katakana,
            length_limit_for_sej,
            ]
        )
    tel_1 = OurTextField(
        label=u"電話番号",
        note=u"(例:09012341234)",
        filters=[ignore_space_hyphen, NFKC],
        validators=[
            SwitchOptional('tel_2'),
            Required(),
            Length(min=1, max=11),
            Regexp(r'^\d*$', message=u'-(ハイフン)を抜いた半角数字のみを入力してください'),
            ]
        )
    tel_2 = OurTextField(
        label=u"電話番号 (携帯)",
        note=u"(例:09012341234)",
        filters=[ignore_space_hyphen, NFKC],
        validators=[
            Optional(),
            Length(min=1, max=11),
            Regexp(r'^\d*$', message=u'-(ハイフン)を抜いた半角数字のみを入力してください'),
            ]
        )
    fax = OurTextField(
        label=u"FAX番号",
        note=u"(ハイフンを除いてご入力ください)",
        filters=[ignore_space_hyphen, NFKC],
        validators=[
            Optional(),
            Length(min=1, max=11),
            Phone(u'FAX番号を確認してください'),
            ]
        )
    zip = OurTextField(
        label=u"郵便番号",
        filters=[ignore_space_hyphen, NFKC],
        validators=[
            Optional(),
            Regexp(r'^\d{7}$', message=u'-(ハイフン)を抜いた半角数字(7桁)のみを入力してください'),
            Length(min=7, max=7, message=u'確認してください'),
            ],
        note=u'(半角英数7ケタ)'
        )
    country = OurSelectField(
        label=u"国・地域",
        filters=[strip_spaces],
        validators=[
            Required(),
            AnyOf(countries, message=u"無効な値、 %(countries)s から選択してください。")
            ]
        )
    prefecture = OurTextField(
        label=u"都道府県",
        filters=[strip_spaces],
        validators=[
            Required()
            ]
        )
    city = OurTextField(
        label=u"市区町村",
        filters=[strip_spaces],
        validators=[
            Required(),
            Length(max=255, message=u'255文字以内で入力してください'),
            CP932,
        ]
    )
    address_1 = OurTextField(
        label=u"町名番地",
        filters=[strip_spaces],
        validators=[
            Required(),
            Length(max=255, message=u'255文字以内で入力してください'),
            CP932,
            ]
        )
    address_2 = OurTextField(
        label=u"建物名等",
        filters=[strip_spaces],
        validators=[
            Length(max=255, message=u'255文字以内で入力してください'),
            CP932,
            ]
        )
    email_1 = OurTextField(
        label=u"メールアドレス",
        note=u"(半角英数)",
        filters=[strip_spaces, NFKC],
        description=lambda field: field._form.context.request.view_context.mail_filter_domain_notice if hasattr(field._form.context.request, 'view_context') else u'',
        validators=[
            Required(),
            SejCompliantEmail(),
            ]
        )
    email_1_confirm = OurTextField(
        label=u"確認",
        filters=[strip_spaces, NFKC],
        validators=[
            Required(),
            SejCompliantEmail(),
            ]
        )
    # XXX: 黒魔術的。email_2 に値が入っていて email_1 に値が入っていなかったら、email_1 に値を移すという動作をする
    email_2 = Liaison(
        email_1,
        OurTextField(
            label=u"メールアドレス",
            filters=[strip_spaces, NFKC],
            validators=[
                SejCompliantEmail(),
                ]
            )
        )
    # XXX: 黒魔術的。email_2_confirm に値が入っていて email_1_confirm に値が入っていなかったら、email_1 に値を移すという動作をする
    email_2_confirm = Liaison(
        email_1_confirm,
        OurTextField(
            label=u"確認",
            filters=[strip_spaces, NFKC],
            validators=[
                SejCompliantEmail(),
                ]
            )
        )

    def __init__(self, formdata=None, obj=None, prefix=u'', **kwargs):
        context = kwargs.pop('context')
        self.context = context
        flavors = kwargs.pop('flavors', {})
        super(ClientForm, self).__init__(formdata, obj, prefix, **kwargs)
        if flavors.get('japanese_prefectures', False):
            self.prefecture.widget = japanese_prefecture_select_input

    def validate_tel_2(self, field):
        if not self.tel_1.data and not self.tel_2.data:
            raise ValidationError(u'電話番号は自宅か携帯かどちらかを入力してください')

    def _validate_email_addresses(self, *args, **kwargs):
        status = True
        data = self.data
        if data["email_1"] != data["email_1_confirm"]:
            getattr(self, "email_1").errors.append(u"メールアドレスと確認メールアドレスが一致していません。")
            status = False
        if data["email_2"] != data["email_2_confirm"]:
            getattr(self, "email_2").errors.append(u"メールアドレスと確認メールアドレスが一致していません。")
            status = False
        return status

    def validate(self):
        # このように and 演算子を展開しないとすべてが一度に評価されない
        status = super(ClientForm, self).validate()
        status = self._validate_email_addresses() and status
        return status
