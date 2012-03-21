from altaircms.models import DBSession
from altaircms.auth.models import Permission

print DBSession.query(Permission).all()

