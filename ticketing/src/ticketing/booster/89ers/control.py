from .schemas import OrderFormSchema

class IndexControl(object):
    def __init__(self, request):
        self.request = request

    def get_form(self):
        return OrderFormSchema


