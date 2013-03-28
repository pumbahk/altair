from markupsafe import Markup

class DispHelper(object):

    @classmethod
    def nl2br(cls, value):
        return value.replace("\n", "<br />")

    @classmethod
    def Markup(cls, value):
        return Markup(value)
