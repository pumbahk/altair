from altaircms.models import DBSession
from deform.form import Form
from . import forms

class UsingFormMixin(object):
    def get_page_form(self):
        return Form(forms.PageSchema(), buttons=("submit", ))

class UsingPageMixin(object):
    pass
    
class SampleCoreResource(UsingPageMixin, UsingFormMixin):
    def __init__(self, request):
        self.request = request
        
    def add(self, data):
        DBSession.add(data)
