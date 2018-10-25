"""add_point_group_and_reason_id_columns

Revision ID: 2ca5bcfe9618
Revises: 1df5975b3586
Create Date: 2018-10-25 10:05:18.099523

"""

# revision identifiers, used by Alembic.
revision = '2ca5bcfe9618'
down_revision = '1df5975b3586'

from alembic import op
import sqlalchemy as sa

Identifier = sa.BigInteger


def upgrade():
    op.add_column('OrganizationSetting', sa.Column('point_group_id', sa.Integer, nullable=True))
    op.add_column('OrganizationSetting', sa.Column('point_reason_id', sa.Integer, nullable=True))


def downgrade():
    op.drop_column('OrganizationSetting', 'point_group_id')
    op.drop_column('OrganizationSetting', 'point_reason_id')
