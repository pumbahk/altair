import pkg_resources
from setuptools import Command

class MigrateCommand(Command):
    description = "run alembic migration"
    user_options = [
        ('config=', 'c', 'config file'),
        ]

    command_consumes_arguments = True
    
    def initialize_options(self, *args, **kwargs):
        self.config = None
        self.args = []

    def finalize_options(self):
        pass

    def run(self):
        runner = pkg_resources.load_entry_point("alembic", "console_scripts", "alembic")
        args = self.args
        runner(['-c', self.config] + args)
