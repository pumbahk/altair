from altaircms.models import Base
from altaircms.models import DBSession
import transaction
from altaircms.page.models import Page

print DBSession.query(Page).all()
