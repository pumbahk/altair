"""update OperatorRole_Operator

Revision ID: 16789909a38
Revises: 166b0db6a45b
Create Date: 2014-03-17 21:34:18.128793

"""

# revision identifiers, used by Alembic.
revision = '16789909a38'
down_revision = '166b0db6a45b'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.execute('UPDATE OperatorRole_Operator SET operator_role_id = 2 WHERE operator_role_id = 1')

def downgrade():
    op.execute('UPDATE OperatorRole_Operator SET operator_role_id = 1 WHERE operator_role_id = 2')
