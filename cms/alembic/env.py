from __future__ import with_statement
from alembic import context
from sqlalchemy import engine_from_config, pool
import sqlahelper
from logging.config import fileConfig

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Pyhton logging. 
# This line sets up loggers basically.
fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
from altaircms import models
from altaircms.asset import models
from altaircms.auth import models
from altaircms.event import models
from altaircms.layout import models
from altaircms.page import models
from altaircms.tag import models
from altaircms.topic import models
from altaircms.usersetting import models
from altaircms.widget import models
# altaircms/widget/tests/models.py

from altaircms.plugins.widget.breadcrumbs import models
from altaircms.plugins.widget.calendar import models
from altaircms.plugins.widget.countdown import models
from altaircms.plugins.widget.detail import models
from altaircms.plugins.widget.flash import models
from altaircms.plugins.widget.freetext import models
from altaircms.plugins.widget.image import models
from altaircms.plugins.widget.menu import models
from altaircms.plugins.widget.movie import models
from altaircms.plugins.widget.performancelist import models
from altaircms.plugins.widget.reuse import models
from altaircms.plugins.widget.summary import models
from altaircms.plugins.widget.ticketlist import models
from altaircms.plugins.widget.topic import models

from altaircms import models
target_metadata = models.Base.metadata
# target_metadata = None

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.
    
    Calls to context.execute() here emit the given string to the
    script output.
    
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url)

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.
    
    """
    engine = engine_from_config(
                config.get_section(config.config_ini_section), 
                prefix='sqlalchemy.', 
                poolclass=pool.NullPool)

    sqlahelper.add_engine(engine)
    connection = engine.connect()
    context.configure(
                connection=connection, 
                target_metadata=target_metadata
                )
    trans = connection.begin()
    try:
        context.run_migrations()
        trans.commit()
    except:
        trans.rollback()
        raise
    try:
        with context.begin_transaction():
            context.run_migrations()
    finally:
        connection.close()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

