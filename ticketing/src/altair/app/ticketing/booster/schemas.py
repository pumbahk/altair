# -*- coding:utf-8 -*-
from wtforms import Form as OriginalForm
from altair.formhelpers import Translations
from wtforms import validators as v

class Form(OriginalForm):
    def _get_translations(self):
        return Translations({
            'This field is required.' : u'入力してください',
            'Not a valid choice' : u'選択してください',
            'Invalid email address.' : u'Emailの形式が正しくありません。',
            'Invalid input.' : u'入力が正しくありません',
        })

length_limit_for_sej = v.Length(max=10, message=u'10文字以内で入力してください')
length_limit_long = v.Length(max=255, message=u'255文字以内で入力してください')
