import argparse
import sqlahelper
import sqlalchemy as sa
import transaction
import ConfigParser
import os

from altaircms.layout.api import LayoutCreator

import altaircms.layout.models
import altaircms.event.models
import altaircms.page.models

def config_proxy(config_file_name):
    if config_file_name:
        here = os.path.abspath(os.path.dirname(config_file_name))
    else:
        here = ""

    file_config = ConfigParser.SafeConfigParser({'here':here})
    file_config.read([config_file_name])
    return file_config

class DummyFileField(object):
    def __init__(self, fname):
        self._original_filename = fname
        self.filename = os.path.splitext(fname)[0]+".mako"
        self.file = open(fname)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", 
                        help="Config file of app")
    parser.add_argument("--ini_section")
    parser.add_argument("-o", "--organization_id")
    parser.add_argument("files", nargs="+")
    args = parser.parse_args()
    return _main(args)

def _main(args):
    config = config_proxy(args.config)
    settings = dict(config.items(args.ini_section))

    engine = sa.create_engine(settings["sqlalchemy.url"])
    engine.echo = True

    sqlahelper.add_engine(engine)
    session = sqlahelper.get_session()

    layout_creator = LayoutCreator(settings["altaircms.layout_directory"])


    for f in args.files:
        params = {"title": os.path.basename(f), 
                  "filepath": DummyFileField(f)}
        layout_creator.create_file(params)
        layout = layout_creator.create_model(params)
        layout.organization_id = args.organization_id
        session.add(layout)

    try:
        transaction.commit()
    except:
        transaction.rollback()
        raise 

main()
