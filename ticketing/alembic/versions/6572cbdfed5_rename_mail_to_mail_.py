"""rename_mail_to_mail_1_and_add_mail_2_for_ShippingAddress_and_UserProfile

Revision ID: 6572cbdfed5
Revises: 48451f969768
Create Date: 2013-01-21 15:11:42.952521

"""

# revision identifiers, used by Alembic.
revision = '6572cbdfed5'
down_revision = '48451f969768'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.alter_column('ShippingAddress', 'email',
        name='email_1',
        existing_type=sa.Unicode(255),
        existing_server_default=text('NULL'),
        existing_nullable=True
        )
    op.alter_column('UserProfile', 'email',
        name='email_1',
        existing_type=sa.Unicode(255),
        existing_server_default=text('NULL'),
        existing_nullable=True
        )
    op.add_column('ShippingAddress',
        sa.Column(
            'email_2',
            sa.Unicode(255),
            nullable=True,
            server_default=text('NULL')
            )
        )
    op.add_column('UserProfile',
        sa.Column(
            'email_2',
            sa.Unicode(255),
            nullable=True,
            server_default=text('NULL')
            )
        )

def downgrade():
    op.alter_column('ShippingAddress', 'email_1',
        name='email',
        existing_type=sa.Unicode(255),
        existing_server_default=text('NULL'),
        existing_nullable=True
        )
    op.alter_column('UserProfile', 'email_1',
        name='email',
        existing_type=sa.Unicode(255),
        existing_server_default=text('NULL'),
        existing_nullable=True
        )
    op.drop_column('ShippingAddress', 'email_2')
    op.drop_column('UserProfile', 'email_2')
