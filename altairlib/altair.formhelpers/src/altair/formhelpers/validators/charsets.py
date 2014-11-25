# encoding: utf-8

import re
from wtforms import validators

HIRAGANAS_REGEXP = ur'ぁ-ゖゝゞー'
KATAKANAS_REGEXP = ur'ァ-ヶヽヾー'
ALPHABETS_REGEXP = ur'a-zA-Zａ-ｚＡ-Ｚ'
NUMERICS_REGEXP = ur'0-9０−９'
ZENKAKU_REGEXP = r"^(?:[\x81-\x9f\xe0-\xfe][\x40-\x7e\x80-\xfc])+$"

Hiragana = validators.Regexp(ur'^[%s]+$' % HIRAGANAS_REGEXP, message=u'ひらがなで入力してください')
Katakana = validators.Regexp(ur'^[%s]+$' % KATAKANAS_REGEXP, message=u'カタカナで入力してください')

class Charset(object):
    def __init__(self, encoding, message=None):
        self.encoding = encoding
        self.message = message or u'利用不可能な文字 (%(characters)s) が含まれています'

    def __call__(self, form, field):
        bad_chars = set()
        bad_chars = self.get_error_chars(field.data)
        if bad_chars:
            raise validators.ValidationError(field.gettext(self.message) % dict(characters=u'「' + u'」「'.join(bad_chars) + u'」'))

    def get_error_chars(self, data):
        return [ch for ch in self.generate_error_chars(data)]

    def generate_error_chars(self, data):
        if data is None:
            return
        for c in data:
            try:
                c.encode(self.encoding)
            except UnicodeEncodeError:
                yield c

ASCII = Charset('ASCII')
JISX0208 = Charset('Shift_JIS')
CP932 = Charset('CP932')

def Zenkaku(form, field):
    try:
        cp932_value = field.data.encode('Shift_JIS')
        if not re.match(ZENKAKU_REGEXP, cp932_value):
            raise Exception()
    except:
        raise validators.ValidationError(field.gettext(u'全角で入力してください'))

def Hankaku(form, field):
    try:
        cp932_value = field.data.encode('Shift_JIS')
        if re.match(ZENKAKU_REGEXP, cp932_value):
            raise Exception()
    except:
        raise validators.ValidationError(field.gettext(u'半角で入力してください'))

