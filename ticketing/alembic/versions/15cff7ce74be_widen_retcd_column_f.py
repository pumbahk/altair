"""widen_retcd_column_for_secure3d_tables

Revision ID: 15cff7ce74be
Revises: 2eb55c0f52e
Create Date: 2014-02-20 22:08:11.817782

"""

# revision identifiers, used by Alembic.
revision = '15cff7ce74be'
down_revision = '2eb55c0f52e'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.alter_column('secure3d_req_enrol_response', 'RetCd',
        type_=sa.Unicode(2),
        existing_type=sa.Unicode(1),
        existing_nullable=True
        )
    op.alter_column('secure3d_req_auth_response', 'RetCd',
        type_=sa.Unicode(2),
        existing_type=sa.Unicode(1),
        existing_nullable=True
        )

def downgrade():
    op.alter_column('secure3d_req_enrol_response', 'RetCd',
        type_=sa.Unicode(1),
        existing_type=sa.Unicode(2),
        existing_nullable=True
        )
    op.alter_column('secure3d_req_auth_response', 'RetCd',
        type_=sa.Unicode(1),
        existing_type=sa.Unicode(2),
        existing_nullable=True
        )
