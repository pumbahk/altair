from zope.interface import Interface
from zope.interface import Attribute

class IBoosterSettings(Interface):
    event_id  = Attribute("target event id")
    membership_name = Attribute("target membership name")


class IPertistentProfileFactory(Interface):
    def __call__(request):
        pass

class IPertistentProfile(Interface):
    def get_userprofile(request, subject):
        pass

    def set_userprofile(request, subject, data):
        pass










## for documantation
class ICartResource(Interface):
    event_id = Attribute("event_id")
    sales_segment_id = Attribute("sales_segment_id")
    organization_id = Attribute("organization id")
    now = Attribute("now") #xxx:
    next = Attribute("next salessegment")
    last = Attribute("last salessegment")
    sales_segment = Attribute("Salessegment object")

    def get_salessegment():
        pass
    def available_sales_segments():
        pass
    def authenticated_user():
        pass
    def _populate_params():
        """initialize attributes. if invalid None is stored"""
    def get_payment_delivery_method_pair(start_at=None):
        pass
    def get_order():
        pass
    
    ## plugin?
    def store_user_profile(data):
        """after product form validation,  validation is success,  store data"""
    def load_user_profile():
        pass
    def remove_user_profile():
        pass
    membership_name = Attribute("membership name")
    product_query = Attribute("query of Product object")
    

class ICartView(Interface):
    context = Attribute("context")
    request = Attribute("request")

class IIndexView(ICartView):
    """ independent of from cart.views.IndexView"""
    ordered_items = Attribute("(ordered_item,  number of item)")
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
