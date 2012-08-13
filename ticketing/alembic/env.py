from __future__ import with_statement
from alembic import context
from sqlalchemy import engine_from_config, pool
from logging.config import fileConfig

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Pyhton logging. 
# This line sets up loggers basically.
fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
from ticketing import models

import ticketing.bj89ers.models
import ticketing.bookmark.models
import ticketing.cart.models
import ticketing.cart.plugins.models
import ticketing.checkout.models
import ticketing.core.models
import ticketing.master.models
import ticketing.models
import ticketing.multicheckout.models
import ticketing.mypage.models
import ticketing.oauth2.models
import ticketing.operators.models
import ticketing.orders.models
import ticketing.sej.models
import ticketing.users.models
import ticketing.tickets.models

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

    connection = engine.connect()
    context.configure(
                connection=connection, 
                target_metadata=target_metadata
                )

    try:
        with context.begin_transaction():
            context.run_migrations()
    finally:
        connection.close()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

