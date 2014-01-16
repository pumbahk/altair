from webhelpers.html.tags import link_to
from .api import get_lotting_announce_timezone

class Link(object):
    def __init__(self, label, url, **attrs):
        self.label = label
        self.url = url
        self.attrs = attrs

    def __html__(self):
        return link_to(self.label, self.url, **self.attrs)

    def __str__(self):
        return self.__html__()

def timezone_label(lot):
    label = ""
    if lot.custom_timezone_label:
        label = lot.custom_timezone_label
    else:
        if lot.lotting_announce_timezone:
            label = get_lotting_announce_timezone(lot.lotting_announce_timezone)
    return label
