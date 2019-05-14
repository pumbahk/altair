"""add table reviewAuthorization

Revision ID: bf3e4743bea
Revises: 2e1dcb75573
Create Date: 2019-03-13 13:33:38.909384

"""

# revision identifiers, used by Alembic.
revision = 'bf3e4743bea'
down_revision = '2e1dcb75573'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.create_table('ReviewAuthorization',
                    sa.Column('id', Identifier, nullable=False),
                    sa.Column('order_no', sa.Unicode(length=255), nullable=False),
                    sa.Column('review_password', sa.String(length=255), nullable=False),
                    sa.Column('email', sa.String(length=255), index=True, nullable=False),
                    sa.Column('type', sa.Boolean(), nullable=False, server_default=text('1')),
                    sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
                    sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
                    sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )

def downgrade():
    op.drop_table('ReviewAuthorization')
