"""add column OperatorRole.organization_id

Revision ID: 427835e63482
Revises: 1328638422b3
Create Date: 2014-03-07 12:21:44.671867

"""

# revision identifiers, used by Alembic.
revision = '427835e63482'
down_revision = '1328638422b3'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('OperatorRole', sa.Column('organization_id', Identifier(), nullable=True))
    op.create_foreign_key('OperatorRole_ibfk_1', 'OperatorRole', 'Organization', ['organization_id'], ['id'])

def downgrade():
    op.drop_constraint('OperatorRole_ibfk_1', 'OperatorRole', 'foreignkey')
    op.drop_column('OperatorRole', 'organization_id')
