# -*- coding:utf-8 -*-
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
from wtforms.validators import Regexp, Length, Optional, EqualTo, AnyOf, Email
from .schemas import length_limit_for_sej
from altair.app.ticketing.i18n import custom_locale_negotiator
countries = [
    u"country_1",u"country_2",u"country_3",u"country_4",u"country_5",u"country_6",u"country_7",u"country_8",u"country_9",u"country_10",u"country_11",u"country_12",u"country_13",u"country_14",u"country_15",u"country_16",u"country_17",u"country_18",u"country_19",u"country_20",
    u"country_21",u"country_22",u"country_23",u"country_24",u"country_25",u"country_26",u"country_27",u"country_28",u"country_29",u"country_30",u"country_31",u"country_32",u"country_33",u"country_34",u"country_35",u"country_36",u"country_37",u"country_38",u"country_39",u"country_40",
    u"country_42",u"country_43",u"country_44",u"country_45",u"country_46",u"country_47",u"country_48",u"country_49",u"country_50",u"country_51",u"country_52",u"country_53",u"country_54",u"country_55",u"country_56",u"country_57",u"country_58",u"country_59",u"country_60",
    u"country_61",u"country_62",u"country_63",u"country_64",u"country_65",u"country_66",u"country_67",u"country_68",u"country_69",u"country_70",u"country_71",u"country_72",u"country_73",u"country_74",u"country_75",u"country_76",u"country_77",u"country_78",u"country_79",u"country_80",
    u"country_81",u"country_82",u"country_83",u"country_84",u"country_85",u"country_86",u"country_87",u"country_88",u"country_89",u"country_90",u"country_91",u"country_92",u"country_93",u"country_94",u"country_95",u"country_96",u"country_97",u"country_98",u"country_99",u"country_100",
    u"country_101",u"country_102",u"country_103",u"country_104",u"country_105",u"country_106",u"country_107",u"country_108",u"country_109",u"country_110",u"country_111",u"country_112",u"country_113",u"country_114",u"country_115",u"country_116",u"country_117",u"country_118",u"country_119",u"country_120",
    u"country_121",u"country_122",u"country_123",u"country_124",u"country_125",u"country_126",u"country_127",u"country_128",u"country_129",u"country_130",u"country_131",u"country_132",u"country_133",u"country_134",u"country_135",u"country_136",u"country_137",u"country_138",u"country_139",u"country_140",
    u"country_141",u"country_142",u"country_143",u"country_144",u"country_145",u"country_146",u"country_147",u"country_148",u"country_149",u"country_150",u"country_151",u"country_152",u"country_153",
]

def get_countries(request):
    _ = request.translate
    return [_(country) for country in countries]

def name_validators(request):
    _ = request.translate
    locale_name = custom_locale_negotiator(request)
    length_limit_for_sej_alphabet = Length(max=20, message=_(u'{0}文字以内で入力してください').format(20))
    base = [Required(_(u'入力してください'))]
    if locale_name == 'ja' or not request.organization.setting.i18n:
        return base + [Zenkaku, length_limit_for_sej]
    if locale_name == 'en':
        return base + [length_limit_for_sej_alphabet, Regexp(r'^[A-z]+$', message=_(u'アルファベットのみを入力してください'))]
    if locale_name == 'zh_CN':
        return base + [length_limit_for_sej_alphabet, Regexp(r'^[A-z]+$', message=_(u'アルファベットのみを入力してください'))]
    if locale_name == 'zh_TW':
        return base + [length_limit_for_sej_alphabet, Regexp(r'^[A-z]+$', message=_(u'アルファベットのみを入力してください'))]
    if locale_name == 'ko':
        return base + [length_limit_for_sej_alphabet, Regexp(r'^[A-z]+$', message=_(u'アルファベットのみを入力してください'))]

def last_name_validators(request):
    return name_validators(request)

def first_name_validators(request):
    return name_validators(request)

def prefecture_validators(request):
    locale_name = custom_locale_negotiator(request)
    _ = request.translate
    base_validators = [Required(_(u'入力してください')), Length(max=64, message=_(u'{0}文字以内で入力してください').format(64))]
    if locale_name == 'ja' or not request.organization.setting.i18n:
        return base_validators + [CP932]
    else:
        return base_validators + [Regexp(r'^[\w\s\.\-,]+$', message=_(u'アルファベット、数字、-(ハイフン)、.(点)、,(コンマ)、空白を入力してください'))]

def city_validators(request):
    locale_name = custom_locale_negotiator(request)
    _ = request.translate
    base_validators = [Required(_(u'入力してください')), Length(max=255, message=_(u'{0}文字以内で入力してください').format(255))]
    if locale_name == 'ja' or not request.organization.setting.i18n:
        return base_validators + [CP932]
    else:
        return base_validators + [Regexp(r'^[\w\s\.\-,]+$', message=_(u'アルファベット、数字、-(ハイフン)、.(点)、,(コンマ)、空白を入力してください'))]

def zip_validators(request):
    locale_name = custom_locale_negotiator(request)
    _ = request.translate
    base_validators = [Regexp(r'^\d{7}$', message=_(u'-(ハイフン)を抜いた半角数字のみを入力してください')), Length(min=7, max=7, message=_(u'確認してください'))]
    if locale_name == 'ja' or not request.organization.setting.i18n:
        return base_validators + [Required(_(u"入力してください"))]
    else:
        return base_validators + [Optional()]

def address_1_validators(request):
    _ = request.translate
    locale_name = custom_locale_negotiator(request)
    base_validators = [Length(max=255, message=_(u'{0}文字以内で入力してください').format(255))]
    if locale_name == 'ja' or not request.organization.setting.i18n:
        return base_validators + [CP932]
    else:
        return base_validators +[Required(_(u'入力してください')), Regexp(r'^[\w\s\.\-,]+$', message=_(u'アルファベット、数字、-(ハイフン)、.(点)、,(コンマ)、空白を入力してください'))]

def address_2_validators(request):
    _ = request.translate
    locale_name = custom_locale_negotiator(request)
    base_validators = [Length(max=255, message=_(u'{0}文字以内で入力してください').format(255))]
    if locale_name == 'ja' or not request.organization.setting.i18n:
        return base_validators + [CP932]
    else:
        return base_validators + [Regexp(r'^[\w\s\.\-,]*$', message=_(u'アルファベット、数字、-(ハイフン)、.(点)、,(コンマ)、空白を入力してください'))]

def mail_validators(request):
    return [SejCompliantEmail()]

def required_mail_validators(request):
    _ = request.translate
    return mail_validators(request) + [Required(_(u'入力してください'))]
