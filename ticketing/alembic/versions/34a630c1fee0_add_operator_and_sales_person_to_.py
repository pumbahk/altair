"""add operator and sales person to performance

Revision ID: 34a630c1fee0
Revises: 2476712e29c7
Create Date: 2017-04-17 16:33:51.622436

"""

# revision identifiers, used by Alembic.
revision = '34a630c1fee0'
down_revision = '2476712e29c7'

from alembic import op
import sqlalchemy as sa

Identifier = sa.BigInteger


def upgrade():
    op.add_column('PerformanceSetting', sa.Column('performance_operator_id', Identifier(), nullable=True))
    op.add_column('PerformanceSetting', sa.Column('sales_person_id', Identifier(), nullable=True))

def downgrade():
    op.drop_column('PerformanceSetting', 'performance_operator_id')
    op.drop_column('PerformanceSetting', 'sales_person_id')
