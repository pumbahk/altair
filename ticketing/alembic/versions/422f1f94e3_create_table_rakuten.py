"""create table RakutenCheckoutSetting

Revision ID: 422f1f94e3
Revises: 136af24cc0c
Create Date: 2013-01-10 11:16:22.591186

"""

# revision identifiers, used by Alembic.
revision = '422f1f94e3'
down_revision = '6572cbdfed5'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.create_table('RakutenCheckoutSetting',
        sa.Column('id', Identifier(), primary_key=True, nullable=False),
        sa.Column('organization_id', Identifier(), nullable=True),
        sa.Column('service_id', sa.Unicode(length=255), nullable=True),
        sa.Column('secret', sa.Unicode(length=255), nullable=True),
        sa.Column('auth_method', sa.Unicode(length=255), nullable=True),
        sa.Column('channel', sa.Integer, nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=None, nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['Organization.id'], name="RakutenCheckoutSetting_ibfk_1"),
        )

def downgrade():
    op.drop_table('RakutenCheckoutSetting')

