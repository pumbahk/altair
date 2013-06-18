from markupsafe import Markup
from datetime import datetime

class DispHelper(object):

    @classmethod
    def nl2br(cls, value):
        return value.replace("\n", "<br />")

    @classmethod
    def Markup(cls, value):
        return Markup(value)

    def now(self):
        return datetime.now()
