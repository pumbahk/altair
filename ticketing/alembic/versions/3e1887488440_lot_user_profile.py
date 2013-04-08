"""lot user profile

Revision ID: 3e1887488440
Revises: 14a36b46cfa7
Create Date: 2013-04-08 16:01:51.306407

"""

# revision identifiers, used by Alembic.
revision = '3e1887488440'
down_revision = '14a36b46cfa7'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('LotEntry', 
                  sa.Column('gender', sa.Integer, server_default=text('0')),
    )
    op.add_column('LotEntry', 
                  sa.Column('birthday', sa.Date),
    )
    op.add_column('LotEntry', 
                  sa.Column('memo', sa.UnicodeText),
    )


def downgrade():
    op.drop_column('LotEntry', 'gender')
    op.drop_column('LotEntry', 'birthday')
    op.drop_column('LotEntry', 'memo')
