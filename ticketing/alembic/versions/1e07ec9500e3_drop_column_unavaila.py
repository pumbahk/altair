"""drop column unavailable_period_days2

Revision ID: 1e07ec9500e3
Revises: 33b55ed26f7c
Create Date: 2013-07-18 13:42:05.459122

"""

# revision identifiers, used by Alembic.
revision = '1e07ec9500e3'
down_revision = '33b55ed26f7c'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.drop_column(u'PaymentDeliveryMethodPair', 'unavailable_period_days2')

def downgrade():
    op.add_column(u'PaymentDeliveryMethodPair', sa.Column('unavailable_period_days2', sa.Integer, nullable=False, default=0))    
