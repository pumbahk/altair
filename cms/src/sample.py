from altaircms.page.models import Page
from altaircms.widget.models import Widget
from altaircms.asset.models import ImageAsset
from altaircms.plugins.widget.image.models import ImageWidget
import transaction

import sqlalchemy as sa
engine = sa.create_engine("sqlite:///")
from altaircms.models import DBSession as S
from altaircms.models import Base
S.configure(bind=engine)
Base.metadata.bind = engine
Base.metadata.create_all()


params = {'description': u'boo',
          'keywords': u'oo',
          'tags': u'ooo',
          'url': u'sample/page',
          'layout_id': 1,
          'title': u'boo',
          # 'structure': u'{}'
          }
page =  Page.from_dict(params)
S.add(page)
transaction.commit()

print Page.query.all()

asset = ImageAsset.from_dict({})
print asset
iw = ImageWidget.from_dict({"asset":asset, "id":1})
S.add(iw)
transaction.commit()
print Widget.query.with_polymorphic([ImageWidget]).all()
page = Page.query.first()
# print Widget.query.all()
# print page.widgets
