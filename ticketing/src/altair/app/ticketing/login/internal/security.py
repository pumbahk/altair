from pyramid.security import remember, forget
import logging
logger = logging.getLogger(__name__)
from altair.app.ticketing.operators.models import Operator

def login(request, login_id, password):
    try:
        assert Operator.login(login_id, password)
        return remember(request, login_id)
    except Exception, e:
        logger.exception(e)
        return None
    
def logout(request):
    return forget(request)

