from altaircms.models import DBSession
from altaircms.asset.models import ImageAsset

print DBSession.query(ImageAsset).all()


