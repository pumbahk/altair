"""Alter PointRedeem change point_status

Revision ID: 523e0f4cc800
Revises: 20876436819d
Create Date: 2018-11-05 19:54:13.328678

"""

# revision identifiers, used by Alembic.
revision = '523e0f4cc800'
down_revision = '20876436819d'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.mysql import TINYINT


def upgrade():
    op.alter_column('PointRedeem', 'point_status', existing_type=TINYINT, type_=sa.SmallInteger, nullable=False)

def downgrade():
    op.alter_column('PointRedeem', 'point_status', existing_type=sa.SmallInteger, type_=TINYINT, nullable=False)
