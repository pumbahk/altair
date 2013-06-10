# -*- coding:utf-8 -*-

from ticketing.views import BaseView
from ..api import load_user_profile, store_user_profile, remove_user_profile
from . import schemas
from webob.multidict import MultiDict
from ticketing.core import models as c_models
import logging
logger = logging.getLogger(__name__)

class IndexView(BaseView):
    def __call__(self):
        return dict()

    def get(self):
        user_profile = load_user_profile(self.request)
        params = schemas.OrderFormSchema, MultiDict(user_profile) if user_profile else MultiDict()
        form = self.context.product_form(params)
        products =  {str(p.id): p for p in  self.context.product_query}
        return dict(form=form, products=products)

