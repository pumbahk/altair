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
        private_tags = [k.strip() for k in params.pop("private_tags").split(",")] ##
        return tags, private_tags, params

    def create(self):
        tags, private_tags, params = self._divide_data()
        page = Page.from_dict(params)
        self.add_tags(page, tags, True)
        self.add_tags(page, private_tags, False)
        return page

    def update(self, page):
        tags, private_tags, params = self._divide_data()
        for k, v in params.iteritems():
            setattr(page, k, v)
        self.add_tags(page, tags, True)
        self.add_tags(page, private_tags, False)
        return page

    def add_tags(self, page, tags, public_status):
        manager = get_tagmanager("page", request=self.request)
        manager.replace(page, tags, public_status)
