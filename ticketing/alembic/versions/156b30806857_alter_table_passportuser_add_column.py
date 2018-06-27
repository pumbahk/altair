"""alter table PassportUser add column

Revision ID: 156b30806857
Revises: 4bd9d32770f5
Create Date: 2018-06-21 18:15:34.900862

"""

# revision identifiers, used by Alembic.
revision = '156b30806857'
down_revision = '4bd9d32770f5'

import sqlalchemy as sa
from alembic import op

Identifier = sa.BigInteger


def upgrade():
    op.add_column('PassportUser', sa.Column('admission_time', sa.TIMESTAMP(), nullable=True))


def downgrade():
    op.drop_column('PassportUser', 'admission_time')
