"""add toggle_enabled to OrionPerformance

Revision ID: 14766315f5ba
Revises: 2cd4d21b8402
Create Date: 2018-03-06 14:26:14.371338

"""

# revision identifiers, used by Alembic.
revision = '14766315f5ba'
down_revision = '2cd4d21b8402'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('OrionPerformance', sa.Column('toggle_enabled', sa.Boolean(), nullable=True))

def downgrade():
    op.drop_column('OrionPerformance', 'toggle_enabled')
