"""add column Refund.organizatoin_id

Revision ID: 10860fae231f
Revises: 46d51164f81f
Create Date: 2014-05-20 15:11:05.633411

"""

# revision identifiers, used by Alembic.
revision = '10860fae231f'
down_revision = '46d51164f81f'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column(u'Refund', sa.Column(u'organization_id', Identifier(), nullable=True))
    op.create_foreign_key(u'Refund_ibfk_2', u'Refund', u'Organization', ['organization_id'], ['id'])
    op.execute('UPDATE Refund, PaymentMethod SET Refund.organization_id = PaymentMethod.organization_id WHERE Refund.payment_method_id = PaymentMethod.id')

def downgrade():
    op.drop_constraint(u'Refund_ibfk_2', u'Refund', 'foreignkey')
    op.drop_column(u'Refund', u'organization_id')
