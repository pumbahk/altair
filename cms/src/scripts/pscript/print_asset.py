from altaircms.models import DBSession
from altaircms.asset.models import ImageAsset

print DBSession.query(ImageAsset).all()
from altaircms.itertools import group_by_n
N = 7
image_assets = group_by_n(DBSession.query(ImageAsset).all(), N)
for g in image_assets:
    print "--"
    for i in g:
        print i


