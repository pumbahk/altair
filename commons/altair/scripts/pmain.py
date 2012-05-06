import argparse
import os
import sys
from pyramid.paster import get_app
from pyramid.paster import bootstrap

def main():
    parser = argparse.ArgumentParser(description="Script eval in pyramid app/env.")
    parser.add_argument("-e", "--env", default="env", 
                        help="Set eval env <app/env> (default: app)")
    parser.add_argument("-c", "--config", 
                        help="Config file of pastedeploy.")
    parser.add_argument("-s", "--script", 
                        help="Script file")
    args = parser.parse_args()

    if not args.config:
        sys.stderr.write("Please provide a configuration file\n")
        sys.exit(255) ## fixme
    config_uri = args.config
    # bootstrap the environ
    if args.env == "app":
        app = get_app(config_uri)
        m = __import__(args.script, globals(), locals(), [args.script.split(".")[-1]])
        return m.main(app)
    else:
        env = bootstrap(config_uri)            
        m = __import__(args.script, globals(), locals(), [args.script.split(".")[-1]])
        return m.main(env)
