import os
from alembic import config as alembic_config
from alembic import util
from alembic.compat import SafeConfigParser
from paste.deploy.loadwsgi import NicerConfigParser
from logging import config as logging_config

class EvenNicerConfigParser(NicerConfigParser):
    def __init__(self, *args, **kwargs):
        NicerConfigParser.__init__(self, *args, **kwargs)
        self._sections_processed = {}

    def get(self, section, option, raw=False, vars=None):
        self._populate_with_variable_assignments(section)
        return NicerConfigParser.get(self, section, option, raw, vars)

    def items(self, section, raw=False, vars=None):
        self._populate_with_variable_assignments(section)
        return NicerConfigParser.items(self, section, raw, vars)

    def options(self, section):
        self._populate_with_variable_assignments(section)
        return NicerConfigParser.options(self, section)

    def remove_section(self, section):
        if section in self._sections_processed:
            del self._sections_processed[section]
        return NicerConfigParser.remove_section(self, section)

    def _populate_with_variable_assignments(self, section):
        if section == 'DEFAULT' or section in self._sections_processed:
            return
        defaults = self.defaults()
        global_vars = dict(defaults)
        self._sections_processed[section] = global_vars
        get_from_globals = {}
        for option in self.options(section):
            if option.startswith('set '):
                name = option[4:].strip()
                global_vars[name] = NicerConfigParser.get(self, section, option)
            elif option.startswith('get '):
                name = option[4:].strip()
                get_from_globals[name] = NicerConfigParser.get(self, section, option)
            else:
                if option in defaults:
                    # @@: It's a global option (?), so skip it
                    continue
                get_from_globals.pop(option, None)
        for lhs, rhs in get_from_globals.items():
            self.set(section, lhs, global_vars[rhs])


class PasteSupportedConfig(alembic_config.Config):
    @util.memoized_property
    def file_config(self):
        if self.config_file_name:
            file_config = EvenNicerConfigParser(self.config_file_name, defaults=self.config_defaults)
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
