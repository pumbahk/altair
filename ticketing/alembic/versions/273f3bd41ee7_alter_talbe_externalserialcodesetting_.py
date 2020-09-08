"""alter talbe ExternalSerialCodeSetting add column

Revision ID: 273f3bd41ee7
Revises: 3f70b09bd2bb
Create Date: 2020-08-27 17:15:53.179162

"""

# revision identifiers, used by Alembic.
revision = '273f3bd41ee7'
down_revision = '3f70b09bd2bb'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('ExternalSerialCodeSetting', sa.Column('organization_id', Identifier(), nullable=True))
    op.add_column('ExternalSerialCodeSetting', sa.Column('url', sa.Text(), nullable=True))


def downgrade():
    op.drop_column('ExternalSerialCodeSetting', 'organization_id')
    op.drop_column('ExternalSerialCodeSetting', 'url')
