from __future__ import with_statement
from alembic import context
from sqlalchemy import engine_from_config, pool

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
from altair.app.ticketing import models

import altair.app.ticketing.bookmark.models
import altair.app.ticketing.cart.models
import altair.app.ticketing.payments.plugins.models
import altair.app.ticketing.checkout.models
import altair.app.ticketing.core.models
import altair.app.ticketing.master.models
import altair.app.ticketing.models
import altair.multicheckout.models
import altair.app.ticketing.mypage.models
import altair.app.ticketing.oauth2.models
import altair.app.ticketing.operators.models
import altair.app.ticketing.sej.models
import altair.app.ticketing.sej.notification.models
import altair.app.ticketing.users.models
import altair.app.ticketing.lots.models
import altair.app.ticketing.lots_admin.models
import altair.app.ticketing.checkinstation.models
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

