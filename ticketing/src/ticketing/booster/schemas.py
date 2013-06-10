# -*- coding:utf-8 -*-
from wtforms import Form as OriginalForm
from ticketing.formhelpers import Translations

class Form(OriginalForm):
    def _get_translations(self):
        return Translations({
            'This field is required.' : u'入力してください',
            'Not a valid choice' : u'選択してください',
            'Invalid email address.' : u'Emailの形式が正しくありません。',
            'Invalid input.' : u'入力が正しくありません',
        })


