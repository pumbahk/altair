from markupsafe import Markup
from altairsite.smartphone.common.helper import SmartPhoneHelper

class DispHelper(object):

    @classmethod
    def nl2br(cls, value):
        return value.replace("\n", "<br />")

    @classmethod
    def Markup(cls, value):
        return Markup(value)

    def get_info(self, event_info, label):
        h = SmartPhoneHelper()
        return h.get_info(event_info=event_info, label=label)

    def get_info_list(self, event_info, label):
        h = SmartPhoneHelper()
        return h.get_info_list(event_info=event_info, label=label)