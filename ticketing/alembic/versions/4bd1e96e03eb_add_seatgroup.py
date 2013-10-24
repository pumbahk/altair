"""add_seatgroup

Revision ID: 4bd1e96e03eb
Revises: 3f1cc8732e9
Create Date: 2013-10-21 23:37:25.252662

"""

# revision identifiers, used by Alembic.
revision = '4bd1e96e03eb'
down_revision = '3f1cc8732e9'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.create_table('SeatGroup',
        sa.Column('id', Identifier(), autoincrement=True, nullable=False),
        sa.Column('name', sa.Unicode(50), nullable=False, default=u""),
        sa.Column('site_id', Identifier(), nullable=False),
        sa.Column('l0_id', sa.Unicode(48), nullable=False),
        sa.Index('ix_SeatGroup_l0_id', 'l0_id', unique=False),
        sa.Index('ix_SeatGroup_site_id_l0_id', 'site_id', 'l0_id', unique=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['site_id'], ['Site.id'], 'SeatGroup_ibfk_1')
        )

def downgrade():
    op.drop_table('SeatGroup')
