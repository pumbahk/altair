from webhelpers.html.tags import link_to


class Link(object):
    def __init__(self, label, url, **attrs):
        self.label = label
        self.url = url
        self.attrs = attrs

    def __html__(self):
        return link_to(self.label, self.url, **self.attrs)

    def __str__(self):
        return self.__html__()

