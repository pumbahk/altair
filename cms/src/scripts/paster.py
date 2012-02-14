# -*- coding:utf-8 -*-
from pyramid.paster import PCommand
from pyramid.paster import get_app
from paste.script import command

class PScript(PCommand):
    """run script on app env.
    """
    summary = "Run script on app env."
    group_name ="Home Made Pyramid script"
    min_args = 2

    parser = command.Command.standard_parser(verbose=True)
    parser.add_option('-E', '--env',
                      action='store', type='string',
                      default='env', help='app | env')
    loaded_objects = {}
    object_help = {}
    setup = None
    
    def command(self):
        config_uri = self.args[0]
        # bootstrap the environ
        if self.options.env == "app":
            app = get_app(config_uri)
            exec(open(self.args[1]))
        else:
            env = self.bootstrap[0](config_uri)            
            exec(open(self.args[1]))


