from altaircms.models import DBSession
from altaircms.models import model_from_dict
from altaircms.models import model_to_dict

from ..flow import api as flow_api
from . import AfterInput

##not good. todo: replace. 
from altaircms.security import RootFactory
class CRUDResource(RootFactory):
    flow_api = flow_api
    def __init__(self, prefix, title, model, form, mapper, endpoint, request):
        self.prefix = prefix
        self.title = title
        self.model = model
        self.form = form
        self.mapper = mapper
        self.endpoint = endpoint
        self.request = request

    def join(self, ac):
        return "%s_%s" % (self.prefix, ac)

    ## create
    def input_form(self):
        return self.form()

    def confirmed_form(self):
        form = self.form(self.request.POST)
        if form.validate():
            return form
        else:
            ## danger
            self.request.matchdict["action"] = "input"
            raise AfterInput(form=form, context=self)
        
    def create_model_from_form(self, form):
        obj = model_from_dict(self.model, form.data)
        DBSession.add(obj)
        return obj

    def get_model_obj(self, id):
        return self.model.query.filter_by(id=id).one()

    ## listing
    def get_model_query(self):
        return self.model.query

    ## update
    def input_form_from_model(self, obj):
        form = self.form(**model_to_dict(obj))
        return form

    update_model_from_form = create_model_from_form

    ## delete
    def delete_model(self, obj):
        DBSession.delete(obj)
