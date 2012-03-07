from pyramid.asset import abspath_from_asset_spec
def main(app):
    path = abspath_from_asset_spec("altaircms:templates/front/original/original.html")
    print open(path).read()
