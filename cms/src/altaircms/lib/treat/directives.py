from interfaces import ICreate
from interfaces import IUpdate

def add_creator(config, adapter, requires=None, name=None):
    """
    use adapter
    """
    config.registry.registerAdapter(adapter, requires, ICreate, name)

def add_updater(config, adapter, requires=None, name=None):
    """
    use adapter
    """
    config.registry.registerAdapter(adapter, requires, IUpdate, name)

