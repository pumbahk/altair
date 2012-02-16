from altaircms.models import DBSession
from altaircms.page.models import Page

print DBSession.query(Page).all()
print [p.url for p in  DBSession.query(Page).all()]

