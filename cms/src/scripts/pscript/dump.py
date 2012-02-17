from altaircms.page.models import Page
from altaircms.widget.generate import WidgetTreeProxy
import pprint

page = Page.query.filter(Page.url=="sample_page").one()
pprint.pprint(page.to_dict())
pprint.pprint(page.layout.to_dict())
config = {"widget.template_path_format": "altaircms:templates/front/widget/%s.mako"}
for block_name, ws in WidgetTreeProxy(page).blocks.items():
    for w in ws:
        pprint.pprint(w.to_dict())

from altaircms.asset.models import ImageAsset

pprint.pprint( ImageAsset.query.first().to_dict())
