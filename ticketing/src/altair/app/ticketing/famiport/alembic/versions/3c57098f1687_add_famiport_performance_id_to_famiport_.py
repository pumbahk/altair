"""add_famiport_performance_id_to_famiport_order

Revision ID: 3c57098f1687
Revises: 12c06bb38ded
Create Date: 2015-08-14 14:37:46.401322

"""

# revision identifiers, used by Alembic.
revision = '3c57098f1687'
down_revision = '12c06bb38ded'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.alter_column('FamiPortOrder', 'famiport_sales_segment_id', nullable=True, existing_type=Identifier, existing_nullable=False)
    op.add_column('FamiPortOrder', sa.Column('famiport_performance_id', Identifier(), nullable=True))
    op.execute('UPDATE FamiPortOrder SET famiport_performance_id=(SELECT famiport_performance_id FROM FamiPortSalesSegment WHERE FamiPortSalesSegment.id=FamiPortOrder.famiport_sales_segment_id);')
    op.alter_column('FamiPortOrder', 'famiport_performance_id', nullable=False, existing_type=Identifier, existing_nullable=True)
    op.create_foreign_key('FamiPortOrder_ibfk_3', 'FamiPortOrder', 'FamiPortPerformance', ['famiport_performance_id'], ['id'])

def downgrade():
    op.drop_constraint('FamiPortOrder_ibfk_3', 'FamiPortOrder', type_='foreignkey')
    op.drop_column('FamiPortOrder', 'famiport_performance_id')
    # op.alter_column('FamiPortOrder', 'famiport_sales_segment_id', nullable=False, existing_type=Identifier, existing_nullable=True)
