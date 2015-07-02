"""alter table Membership add column display_name

Revision ID: 38e00b9843c3
Revises: 4ab26bf2ebf2
Create Date: 2015-06-26 17:23:06.293296

"""

# revision identifiers, used by Alembic.
revision = '38e00b9843c3'
down_revision = '4ab26bf2ebf2'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('Membership', sa.Column('display_name', sa.Unicode(length=255), nullable=True))

def downgrade():
    op.drop_column('Membership', u'display_name')
