"""alter table Performance add column account_id

Revision ID: 1604dd750140
Revises: 51227242a955
Create Date: 2016-06-07 15:31:55.869975

"""

# revision identifiers, used by Alembic.
revision = '1604dd750140'
down_revision = '51227242a955'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column(u'Performance', sa.Column(u'account_id', Identifier(), sa.ForeignKey('Account.id', name='Performance_ibfk_2'), nullable=True))

def downgrade():
    op.drop_constraint('Performance_ibfk_2', 'Performance', type='foreignkey')
    op.drop_column(u'Performance', u'account_id')
