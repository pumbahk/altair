import logging
import sys
from pyramid.paster import bootstrap, setup_logging
from cliff.app import App
from cliff.commandmanager import CommandManager

logger = logging.getLogger(__name__)

class Application(App):

    def __init__(self):
        super(Application, self).__init__(
            description='altair mq worker service',
            version='0.1',
            command_manager=CommandManager('altair.mq.command'),
            )

    def build_option_parser(self, description, version, argparse_kwargs=None):
        parser = super(Application, self).build_option_parser(description, version, argparse_kwargs)
        parser.add_argument("config")
        return parser

    def initialize_app(self, argv):
        logger.debug('initialize_app')
        self.config_uri = self.options.config

    def prepare_to_run_command(self, cmd):
        logger.debug('prepare_to_run_command %s', cmd.__class__.__name__)
        self.app = bootstrap(self.config_uri)
        setup_logging(self.config_uri)

    def clean_up(self, cmd, result, err):
        logger.debug('clean_up %s', cmd.__class__.__name__)
        if err:
            logger.debug('got an error: %s', err)



def main(argv=sys.argv[1:]):
    myapp = Application()
    return myapp.run(argv)
