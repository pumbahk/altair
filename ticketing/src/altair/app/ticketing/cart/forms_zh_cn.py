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

countries = [
    u'日本',
    u'阿尔及利亚', u'安哥拉', u'亚美尼亚', u'阿塞拜疆', u'澳大利亚', u'阿尔巴尼亚', u'奥地利', u'安圭拉', u'安提瓜和巴布达', u'阿根廷',
    u'巴林', u'贝宁', u'博茨瓦纳', u'布基纳法索', u'不丹', u'文莱达鲁萨兰国', u'白俄罗斯', u'比利时', u'保加利亚', u'巴哈马', u'巴巴多斯', u'伯利兹', u'百慕大', u'玻利维亚', u'巴西',
    u'佛得角', u'乍得', u'刚果共和国', u'柬埔寨', u'中国', u'克罗地亚', u'捷克共和国', u'塞浦路斯', u'开曼群岛', u'智利', u'哥伦比亚', u'哥斯达黎加', u'加拿大',
    u'多米尼加', u'多明尼加',
    u'德国',
    u'埃及', u'爱沙尼亚', u'厄瓜多尔', u'萨尔瓦多',
    u'斐济', u'法国', u'芬兰',
    u'冈比亚', u'加纳', u'几内亚比绍', u'希腊', u'格林纳达', u'危地马拉', u'圭亚那',
    u'香港', u'匈牙利', u'洪都拉斯',
    u'印度', u'以色列', u'印度尼西亚', u'冰岛', u'爱尔兰', u'意大利',
    u'约旦', u'牙买加',
    u'肯尼亚', u'科威特', u'哈萨克斯坦', u'韩国', u'吉尔吉斯斯坦',
    u'利比里亚', u'老挝', u'黎巴嫩', u'拉脱维亚', u'立陶宛', u'卢森堡',
    u'马达加斯加', u'马拉维', u'马里', u'毛里塔尼亚', u'毛里求斯', u'莫桑比克', u'澳门', u'马来西亚', u'密克罗尼西亚联邦国家', u'蒙古', u'马其顿', u'马耳他', u'摩尔多瓦', u'墨西哥', u'蒙特塞拉特',
    u'纳米比亚', u'尼日尔', u'尼日利亚', u'尼泊尔', u'新西兰', u'荷兰', u'挪威', u'尼加拉瓜',
    u'阿曼', u'卡塔尔',
    u'巴基斯坦', u'帕劳', u'巴布亚新几内亚', u'菲律宾', u'波兰', u'葡萄牙', u'巴拿马', u'巴拉圭', u'秘鲁',
    u'罗马尼亚', u'俄国',
    u'圣多美和普林西比', u'沙特阿拉伯', u'塞内加尔', u'塞舌尔', u'塞拉利昂', u'南非', u'斯威士兰', u'新加坡', u'所罗门群岛', u'斯里兰卡', u'西班牙', u'瑞士', u'斯洛伐克', u'斯洛文尼亚', u'瑞典', u'圣基茨和尼维斯', u'圣卢西亚', u'圣文森特和格林纳丁斯', u'苏里南',
    u'坦桑尼亚', u'突尼斯', u'台湾', u'塔吉克斯坦', u'泰国', u'土库曼斯坦', u'土耳其', u'特立尼达和多巴哥', u'特克斯和凯科斯群岛',
    u'乌干达', u'阿拉伯联合酋长国', u'乌兹别克斯坦', u'英国', u'乌拉圭', u'美国',
    u'越南', u'委内瑞拉', u'维尔京群岛',
    u'也门',
    u'津巴布韦'
]

length_limit_for_sej_cn = Length(max=20, message=u'请输入长度小于20的拼音字母')
class ClientForm(OurDynamicForm):
    """国際化の簡体中国語フォーム"""
    def _get_translations(self):
        return Translations()

    last_name = OurTextField(
        label=u"姓",
        filters=[strip_spaces],
        validators=[
            Required(u'请输入'),
            length_limit_for_sej_cn,
            Regexp(r'^[A-z]+$', message=u'请输入与护照等身份证件一致的拼音拼写'),
            ],
        )
    first_name = OurTextField(
        label=u"名",
        filters=[strip_spaces],
        validators=[
            Required(u'请输入'),
            length_limit_for_sej_cn,
            Regexp(r'^[A-z]+$', message=u'请输入与护照等身份证件一致的拼音拼写'),
            ]
        )
    tel_1 = OurTextField(
        label=u"电话号码",
        filters=[ignore_space_hyphen, NFKC],
        validators=[
            SwitchOptional('tel_2'),
            Required(u'请输入'),
            Length(min=1, max=11),
            Regexp(r'^\d*$', message=u'请输入连续的数字（不用破折号）'),
            ]
        )
    tel_2 = OurTextField(
        label=u"电话号码2",
        filters=[ignore_space_hyphen, NFKC],
        validators=[
            Optional(),
            Length(min=1, max=11),
            Regexp(r'^\d*$', message=u'请输入连续的数字（不用破折号）'),
            ]
        )
    fax = OurTextField(
        label=u"传真",
        filters=[ignore_space_hyphen, NFKC],
        validators=[
            Optional(),
            Length(min=1, max=11),
            Phone(u'请检查传真号码'),
            ]
        )
    zip = OurTextField(
        label=u"邮政编码",
        filters=[ignore_space_hyphen, NFKC],
        validators=[
            Optional(),
            Regexp(r'^\d{7}$', message=u'请输入不带破折号的7位数字'),
            Length(min=7, max=7, message=u'请检查'),
            ]
        )
    country = OurSelectField(
        label=u"国家／地区",
        filters=[strip_spaces],
        validators=[
            Required(u'请输入'),
            AnyOf(countries, message=u"请输入以下的值: %(countries)s")
            ]
        )
    prefecture = OurTextField(
        label=u"省／都道府县",
        filters=[strip_spaces],
        validators=[
            Required(u'请输入'),
            ]
        )
    city = OurTextField(
        label=u"市／区",
        filters=[strip_spaces],
        validators=[
            Required(u'请输入'),
            Length(max=255, message=u'请输入255字符以内的文字'),
        ]
    )
    address_1 = OurTextField(
        label=u"路／号",
        filters=[strip_spaces],
        validators=[
            Required(u'请输入'),
            Length(max=255, message=u'请输入255字符以内的文字'),
            ]
        )
    address_2 = OurTextField(
        label=u"建筑物等",
        filters=[strip_spaces],
        validators=[
            Length(max=255, message=u'请输入255字符以内的文字'),
            ]
        )
    email_1 = OurTextField(
        label=u"电子邮件",
        filters=[strip_spaces, NFKC],
        description=lambda field: field._form.context.request.view_context.mail_filter_domain_notice if hasattr(field._form.context.request, 'view_context') else u'',
        validators=[
            Required(u'请输入'),
            Email(u'请输入正确电子邮件格式'),
            ]
        )
    email_1_confirm = OurTextField(
        label=u"确认用",
        filters=[strip_spaces, NFKC],
        validators=[
            Required(u'请输入'),
            Email(u'请输入正确电子邮件格式'),
            ]
        )
    email_2 = Liaison(
        email_1,
        OurTextField(
            label=u"电子邮件2",
            filters=[strip_spaces, NFKC],
            validators=[
                SejCompliantEmail(),
                ]
            )
        )
    email_2_confirm = Liaison(
        email_1_confirm,
        OurTextField(
            label=u"确认用",
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
            raise ValidationError(u'请输入住宅或手机号码')

    def _validate_email_addresses(self, *args, **kwargs):
        status = True
        data = self.data
        if data["email_1"] != data["email_1_confirm"]:
            getattr(self, "email_1").errors.append(u"电子邮件地址和确认用的地址不一致")
            status = False
        if data["email_2"] != data["email_2_confirm"]:
            getattr(self, "email_2").errors.append(u"电子邮件地址和确认用的地址不一致")
            status = False
        return status

    def validate(self):
        status = super(ClientForm, self).validate()
        status = self._validate_email_addresses() and status
        return status
