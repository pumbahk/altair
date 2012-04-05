from altaircms.lib.treat.decorators import creator_from_form
from altaircms.lib.treat.decorators import updater_from_form
from .models import Page
from altaircms.tag.api import get_tagmanager

@updater_from_form(name="page", use_request=True)
@creator_from_form(name="page", use_request=True)
class PageTreatAdapter(object):
    def __init__(self, form, request=None):
        self.form = form
        self.request = request

    def _divide_data(self):
        params = dict(self.form.data)
        tags = [k.strip() for k in params.pop("tags").split(",")] ##
        return tags, params

    def create(self):
        tags, params = self._divide_data()
        page = Page.from_dict(params)
        self.add_tags(page, tags)
        return page

    def update(self, page):
        tags, params = self._divide_data()
        for k, v in params.iteritems():
            setattr(page, k, v)
        self.add_tags(page, tags)
        return page

    def add_tags(self, page, tags):
        manager = get_tagmanager("page", request=self.request)
        manager.replace(page, tags)
