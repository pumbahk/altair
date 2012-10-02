from pyramid.security import remember, forget
import logging
logger = logging.getLogger(__name__)
from ticketing.operators.models import Operator

def login(request, login_id, password):
    try:
        operator = Operator.login(login_id, password)
        return remember(request, login_id)
    except Exception, e:
        logger.exception(e)
        return None
    
def logout(request):
    return forget(request)

def find_group(user_id, request):
    return ["group:sales_counter"]
