"""alter table EventSetting add column tapirs

Revision ID: 79706bc2912
Revises: 1f9dae4d0c08
Create Date: 2017-08-30 11:45:42.885802

"""

# revision identifiers, used by Alembic.
revision = '79706bc2912'
down_revision = '1f9dae4d0c08'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('EventSetting',
                  sa.Column('tapirs', sa.Boolean(), nullable=True, default=False, server_default=text('0')))
    op.add_column('OrganizationSetting',
                  sa.Column('tapirs', sa.Boolean(), nullable=True, default=False, server_default=text('0')))


def downgrade():
    op.drop_column('EventSetting', 'tapirs')
    op.drop_column('OrganizationSetting', 'tapirs')
