# -*- coding:utf-8 -*-
from altair.formhelpers.translations import Translations
from altair.formhelpers.form import OurForm, OurDynamicForm
from wtforms.validators import Regexp, Length, Optional, EqualTo, Email, AnyOf
from altair.formhelpers.validators import (
    Required,
    Phone,
    SejCompliantEmail,
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
    u'阿爾及利亞', u'安哥拉', u'亞美尼亞', u'阿塞拜疆', u'澳大利亞', u'阿爾巴尼亞', u'奧地利', u'安圭拉', u'安提瓜和巴布達', u'阿根廷',
    u'巴林', u'貝寧', u'博茨瓦納', u'布基納法索', u'不丹', u'文萊達魯薩蘭國', u'白俄羅斯', u'比利時', u'保加利亞', u'巴哈馬', u'巴巴多斯', u'伯利茲', u'百慕大', u'玻利維亞', u'巴西',
    u'佛得角', u'乍得', u'剛果共和國', u'柬埔寨', u'中國', u'克羅地亞', u'捷克共和國', u'塞浦路斯', u'開曼群島', u'智利', u'哥倫比亞', u'哥斯達黎加', u'加拿大',
    u'多米尼加', u'多明尼加',
    u'德國',
    u'埃及', u'愛沙尼亞', u'厄瓜多爾', u'薩爾瓦多',
    u'斐濟', u'法國', u'芬蘭',
    u'岡比亞', u'加納', u'幾內亞比紹', u'希臘', u'格林納達', u'危地馬拉', u'圭亞那',
    u'香港', u'匈牙利', u'洪都拉斯',
    u'印度', u'以色列', u'印度尼西亞', u'冰島', u'愛爾蘭', u'意大利',
    u'約旦', u'牙買加',
    u'肯尼亞', u'科威特', u'哈薩克斯坦', u'韓國', u'吉爾吉斯斯坦',
    u'利比里亞', u'老撾', u'黎巴嫩', u'拉脫維亞', u'立陶宛', u'盧森堡',
    u'馬達加斯加', u'馬拉維', u'馬里', u'毛里塔尼亞', u'毛里求斯', u'莫桑比克', u'澳門', u'馬來西亞', u'密克羅尼西亞聯邦國家', u'蒙古', u'馬其頓', u'馬耳他', u'摩爾多瓦', u'墨西哥', u'蒙特塞拉特',
    u'納米比亞', u'尼日爾', u'尼日利亞', u'尼泊爾', u'新西蘭', u'荷蘭', u'挪威', u'尼加拉瓜',
    u'阿曼', u'卡塔爾',
    u'巴基斯坦', u'帕勞', u'巴布亞新幾內亞', u'菲律賓', u'波蘭', u'葡萄牙', u'巴拿馬', u'巴拉圭', u'秘魯',
    u'羅馬尼亞', u'俄國',
    u'聖多美和普林西比', u'沙特阿拉伯', u'塞內加爾', u'塞舌爾', u'塞拉利昂', u'南非', u'斯威士蘭', u'新加坡', u'所羅門群島', u'斯里蘭卡', u'西班牙', u'瑞士', u'斯洛伐克', u'斯洛文尼亞', u'瑞典', u'聖基茨和尼維斯', u'聖盧西亞', u'聖文森特和格林納丁斯', u'蘇里南',
    u'坦桑尼亞', u'突尼斯', u'台灣', u'塔吉克斯坦', u'泰國', u'土庫曼斯坦', u'土耳其', u'特立尼達和多巴哥', u'特克斯和凱科斯群島',
    u'烏干達', u'阿拉伯聯合酋長國', u'烏茲別克斯坦', u'英國', u'烏拉圭', u'美國',
    u'越南', u'委內瑞拉', u'維爾京群島',
    u'也門',
    u'津巴布韋'
]

length_limit_for_sej_tw = Length(max=20, message=u'请输入长度小于20的拼音字母')
class ClientForm(OurDynamicForm):
    """国際化の繁体中国語フォーム"""
    def _get_translations(self):
        return Translations()

    last_name = OurTextField(
        label=u"姓",
        filters=[strip_spaces],
        validators=[
            Required(u'請輸入'),
            length_limit_for_sej_tw,
            Regexp(r'^[A-z]+$', message=u'请输入与护照等身份证件一致的拼音拼写'),
            ],
        )
    first_name = OurTextField(
        label=u"名",
        filters=[strip_spaces],
        validators=[
            Required(u'請輸入'),
            length_limit_for_sej_tw,
            Regexp(r'^[A-z]+$', message=u'请输入与护照等身份证件一致的拼音拼写'),
            ]
        )
    tel_1 = OurTextField(
        label=u"電話號碼",
        filters=[ignore_space_hyphen, NFKC],
        validators=[
            SwitchOptional('tel_2'),
            Required(u'請輸入'),
            Length(min=1, max=11),
            Regexp(r'^\d*$', message=u'請輸入唯一的單字節數斷開（連字符）'),
            ]
        )
    tel_2 = OurTextField(
        label=u"電話號碼2",
        filters=[ignore_space_hyphen, NFKC],
        validators=[
            Optional(),
            Length(min=1, max=11),
            Regexp(r'^\d*$', message=u'請輸入唯一的單字節數斷開（連字符）'),
            ]
        )
    fax = OurTextField(
        label=u"傳真號碼",
        filters=[ignore_space_hyphen, NFKC],
        validators=[
            Optional(),
            Length(min=1, max=11),
            Phone(u'請檢查傳真號碼'),
            ]
        )
    zip = OurTextField(
        label=u"郵政編碼",
        filters=[ignore_space_hyphen, NFKC],
        validators=[
            Optional(),
            Regexp(r'^\d{7}$', message=u'請輸入唯一的單字節數斷開（連字符）（7位數）'),
            Length(min=7, max=7, message=u'請檢查'),
            ]
        )
    country = OurSelectField(
        label=u"國家/區域",
        filters=[strip_spaces],
        validators=[
            Required(u'請輸入'),
            AnyOf(countries, message=u"無效值。請從下列選擇： %(countries)s")
            ]
        )
    prefecture = OurTextField(
        label=u"專區／都道府県",
        filters=[strip_spaces],
        validators=[
            Required(u'請輸入'),
            ]
        )
    city = OurTextField(
        label=u"市／区",
        filters=[strip_spaces],
        validators=[
            Required(u'請輸入'),
            Length(max=255, message=u'請輸入最多255個字符'),
        ]
    )
    address_1 = OurTextField(
        label=u"路／号",
        filters=[strip_spaces],
        validators=[
            Required(u'請輸入'),
            Length(max=255, message=u'請輸入最多255個字符'),
            ]
        )
    address_2 = OurTextField(
        label=u"建筑物等",
        filters=[strip_spaces],
        validators=[
            Length(max=255, message=u'請輸入最多255個字符'),
            ]
        )
    email_1 = OurTextField(
        label=u"電子郵件",
        filters=[strip_spaces, NFKC],
        description=lambda field: field._form.context.request.view_context.mail_filter_domain_notice if hasattr(field._form.context.request, 'view_context') else u'',
        validators=[
            Required(u'請輸入'),
            Email(u'請輸入正確的格式電子郵件'),
            ]
        )
    email_1_confirm = OurTextField(
        label=u"確認用",
        filters=[strip_spaces, NFKC],
        validators=[
            Required(u'請輸入'),
            Email(u'請輸入正確的格式電子郵件'),
            ]
        )
    email_2 = Liaison(
        email_1,
        OurTextField(
            label=u"電子郵件2",
            filters=[strip_spaces, NFKC],
            validators=[
                SejCompliantEmail(),
                ]
            )
        )
    email_2_confirm = Liaison(
        email_1_confirm,
        OurTextField(
            label=u"確認用",
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
            raise ValidationError(u'電話號碼，請輸入兩個或移動或家庭')

    def _validate_email_addresses(self, *args, **kwargs):
        status = True
        data = self.data
        if data["email_1"] != data["email_1_confirm"]:
            getattr(self, "email_1").errors.append(u"E-mail地址，並確認電子郵件地址不匹配")
            status = False
        if data["email_2"] != data["email_2_confirm"]:
            getattr(self, "email_2").errors.append(u"E-mail地址，並確認電子郵件地址不匹配")
            status = False
        return status

    def validate(self):
        status = super(ClientForm, self).validate()
        status = self._validate_email_addresses() and status
        return status
