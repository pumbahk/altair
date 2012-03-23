import os
here = os.path.abspath(os.path.dirname(__file__))

def add_initial_junk_data():
    assetpath = os.path.join(here, "asset")
    if not os.path.exists(assetpath):
        os.makedirs(assetpath)
    from . import initialize
    initialize.init()
