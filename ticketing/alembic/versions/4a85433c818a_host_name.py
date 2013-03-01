"""Host.name

Revision ID: 4a85433c818a
Revises: 5278077a5232
Create Date: 2013-02-18 17:58:36.275165

"""

# revision identifiers, used by Alembic.
revision = '4a85433c818a'
#down_revision = '5278077a5232'
down_revision = '209a1863fc22'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.drop_constraint('host_name', 'Host', type="unique")
    op.add_column('Host',
        sa.Column('path', sa.Unicode(255)),
    )
    op.create_unique_constraint('host_name_path', 'Host', ['host_name', 'path'])
        

def downgrade():
    op.drop_constraint('host_name_path', 'Host', type="unique")
    op.drop_column('Host', 'path')
    op.create_unique_constraint('host_name', 'Host', ['host_name'])
