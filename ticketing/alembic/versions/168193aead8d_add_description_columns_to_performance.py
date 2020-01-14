"""Add description columns to Performance.

Revision ID: 168193aead8d
Revises: 294ca5bb74d2
Create Date: 2019-11-27 13:24:55.327706

"""

# revision identifiers, used by Alembic.
revision = '168193aead8d'
down_revision = '294ca5bb74d2'

from alembic import op
import sqlalchemy as sa

Identifier = sa.BigInteger


def upgrade():
    op.add_column('Performance', sa.Column('description1', sa.String(2000), nullable=True))
    op.add_column('Performance', sa.Column('description2', sa.String(2000), nullable=True))


def downgrade():
    op.drop_column('Performance', 'description1')
    op.drop_column('Performance', 'description2')
