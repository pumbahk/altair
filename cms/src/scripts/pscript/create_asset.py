from altaircms.models import DBSession
from altaircms.asset.treat import create_asset
from pyramid.asset import abspath_from_asset_spec

types = ["image", "flash", "movie"]
fnames = ["altaircms:static/blueman.jpg","altaircms:static/blueman.swf", ]
fnames = [abspath_from_asset_spec(f) for f in fnames]
for asset_type, fname in zip(types, fnames):
    captured = dict(type=asset_type, 
                    uploadfile=dict(filename=fname, 
                                    fp = open(fname, "rb")))
    DBSession.add(create_asset(captured))

import transaction
transaction.commit()
