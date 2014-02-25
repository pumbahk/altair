import os
from alembic import config as alembic_config
from alembic import util
from alembic.compat import SafeConfigParser
from paste.deploy.loadwsgi import NicerConfigParser
from logging import config as logging_config

class PasteSupportedConfig(alembic_config.Config):
    @util.memoized_property
    def file_config(self):
        if self.config_file_name:
            file_config = NicerConfigParser(self.config_file_name, defaults=self.config_defaults)
            file_config.read(self.config_file_name)
        else:
            file_config = SafeConfigParser(self.config_defaults)
            file_config.add_section(self.config_ini_section)
        return file_config

    @util.memoized_property
    def config_defaults(self):
        if self.config_file_name:
            here = os.path.abspath(os.path.dirname(self.config_file_name))
            file__ = os.path.abspath(self.config_file_name)
        else:
            here = ''
            file__ = ''
        return {'here': here, '__file__': file__}

class PasteSupportedCommandLine(alembic_config.CommandLine):
    def main(self, argv=None, setup_logging=False):
        options = self.parser.parse_args(argv)
        if not hasattr(options, "cmd"):
            self.parser.error("too few arguments")
        else:
            cfg = PasteSupportedConfig(
                file_=options.config,
                ini_section=options.name,
                cmd_opts=options
                )
            if setup_logging:
                logging_config.fileConfig(
                    cfg.config_file_name,
                    cfg.config_defaults
                    )
            self.run_cmd(cfg, options)

def main(argv=None, prog=None, **kwargs):
    PasteSupportedCommandLine(prog=prog).main(argv=argv, setup_logging=True)