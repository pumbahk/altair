"""adjust_prefecture_column_length

Revision ID: 43c53ca49806
Revises: 54385b1b2cdf
Create Date: 2014-01-21 10:10:01.220979

"""

# revision identifiers, used by Alembic.
revision = '43c53ca49806'
down_revision = '54385b1b2cdf'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.alter_column(
        'Organization', 'prefecture',
        type_=sa.Unicode(64),
        nullable=False,
        server_default=u'',
        existing_type=sa.String(255),
        existing_nullable=True,
        existing_server_default=text('NULL')
        )
    op.alter_column(
        'ShippingAddress', 'zip',
        type_=sa.Unicode(32),
        existing_type=sa.String(255),
        existing_nullable=True,
        existing_server_default=text('NULL')
        )
    op.alter_column(
        'ShippingAddress', 'prefecture',
        type_=sa.Unicode(64),
        existing_type=sa.String(255),
        existing_nullable=False,
        existing_server_default=u''
        )
    op.alter_column(
        'UserProfile', 'zip',
        type_=sa.Unicode(32),
        existing_type=sa.String(255),
        existing_nullable=True,
        existing_server_default=text('NULL')
        )
    op.alter_column(
        'Site', 'zip',
        type_=sa.Unicode(32),
        existing_type=sa.String(255),
        existing_nullable=True,
        existing_server_default=text('NULL')
        )
    op.alter_column(
        'Site', 'prefecture',
        type_=sa.Unicode(64),
        existing_type=sa.String(255),
        existing_nullable=True,
        existing_server_default=text('NULL')
        )

def downgrade():
    op.alter_column(
        'Organization', 'prefecture',
        type_=sa.String(255),
        nullable=True,
        server_default=text('NULL'),
        existing_type=sa.Unicode(64),
        existing_nullable=False,
        existing_server_default=u''
        )
    op.alter_column(
        'ShippingAddress', 'zip',
        type_=sa.String(255),
        existing_type=sa.Unicode(32),
        existing_nullable=True,
        existing_server_default=text('NULL')
        )
    op.alter_column(
        'ShippingAddress', 'prefecture',
        type_=sa.String(255),
        existing_type=sa.Unicode(64),
        existing_nullable=False,
        existing_server_default=u''
        )
    op.alter_column(
        'UserProfile', 'zip',
        type_=sa.String(255),
        existing_type=sa.Unicode(32),
        existing_nullable=True,
        existing_server_default=text('NULL')
        )
    op.alter_column(
        'Site', 'zip',
        type_=sa.Unicode(32),
        existing_type=sa.String(255),
        existing_nullable=True,
        existing_server_default=text('NULL')
        )
    op.alter_column(
        'Site', 'prefecture',
        type_=sa.String(255),
        existing_type=sa.Unicode(64),
        existing_nullable=True,
        existing_server_default=text('NULL')
        )
