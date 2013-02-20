"""Product.performance

Revision ID: 5311fff7b14a
Revises: 7bbb00f130
Create Date: 2013-01-29 16:59:35.299483

"""

# revision identifiers, used by Alembic.
revision = '5311fff7b14a'
down_revision = '7bbb00f130'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('Product', 
        sa.Column('performance_id', Identifier, sa.ForeignKey('Performance.id')),
        )

def downgrade():
    op.drop_column('Product', 'performance_id')
