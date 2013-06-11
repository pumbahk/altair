from zope.interface import Interface
from zope.interface import Attribute

class IBoosterSettings(Interface):
    event_id  = Attribute("target event id")
    membership_name = Attribute("target membership name")


## for documantation
class ICartResource(Interface):
    event_id = Attribute("event_id")
    now = Attribute("now") #xxx:
    next = Attribute("next salessegment")
    last = Attribute("last salessegment")
    sales_segment = Attribute("salessegment object")
    def authenticated_user():
        pass


class ICartView(Interface):
    context = Attribute("context")
    request = Attribute("request")

class IIndexView(ICartView):
    """ independent of from cart.views.IndexView"""
    ordered_items = Attribute("a pair of (ordered_item,  number of item)")
    def get():
        pass
    def post():
        pass

class IPaymentView(ICartView):
    def get():
        pass
    def post():
        pass

    sales_segment = Attribute("matched correct salessegment object")

    ## notice. this attribute is created in self.post()
    form = Attribute("ClientForm")

    def get_validated_address_data():
        """[maybe] shipping address data from form"""

    def create_shipping_address(user, data):
        """(user, data) -> Model"""

    def get_client_name():
        """()  -> String"""

    def _validate_extras(cart, pdmp, shipping_address_params):
        """() -> Boolean"""
        
    
class ICompleteView(ICartView):
    def __call__():
        pass

class IOrderReviewView(ICartView):
    order_not_found_message = Attribute("[string]")
    def get():
        pass

    def post():
        pass
