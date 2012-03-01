from altaircms.models import DBSession
from altaircms.page.models import Page

print DBSession.query(Page).all()
page = DBSession.query(Page).first()
print [e[0] for e in page.column_items()]
print page.widgets
print page.structure
print [p.url for p in  DBSession.query(Page).all()]

