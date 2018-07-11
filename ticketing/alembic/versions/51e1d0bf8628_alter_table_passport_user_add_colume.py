"""alter table Passport User add colume

Revision ID: 51e1d0bf8628
Revises: 156b30806857
Create Date: 2018-07-06 11:35:01.934421

"""

# revision identifiers, used by Alembic.
revision = '51e1d0bf8628'
down_revision = '156b30806857'

import sqlalchemy as sa
from alembic import op

Identifier = sa.BigInteger


def upgrade():
    op.add_column(u'PassportUser', sa.Column('confirmed_at', sa.TIMESTAMP(), nullable=True))


def downgrade():
    op.drop_column(u'PassportUser', 'confirmed_at')
