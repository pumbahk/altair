"""#tkt621 add subtitle2, subtitle3 to Performance

Revision ID: 38b6b43b7e5d
Revises: 566dd0ea18db
Create Date: 2015-12-11 15:34:28.053120

"""

# revision identifiers, used by Alembic.
revision = '38b6b43b7e5d'
down_revision = '566dd0ea18db'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('Performance', sa.Column('subtitle2', sa.Unicode(length=255), nullable=True))
    op.add_column('Performance', sa.Column('subtitle3', sa.Unicode(length=255), nullable=True))
    op.add_column('Performance', sa.Column('subtitle4', sa.Unicode(length=255), nullable=True))

def downgrade():
    op.drop_column('Performance', 'subtitle2')
    op.drop_column('Performance', 'subtitle3')
    op.drop_column('Performance', 'subtitle4')
