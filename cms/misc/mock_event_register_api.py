from pyramid.paster import bootstrap
import sys
import json

def main(args):
    configfile = args[1]
    jsonfile = args[2]
    env = bootstrap(configfile)
    from altaircms.event.api import parse_and_save_event
    with open(jsonfile) as rf:
        jsondata = json.load(rf)
    parse_and_save_event(env["request"], jsondata)
    import transaction
    transaction.commit()
    
main(sys.argv)
