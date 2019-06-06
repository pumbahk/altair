"""modify_PGWMaskedCardDetail_table

Revision ID: 28883f040e44
Revises: 54ed57d1575b
Create Date: 2019-06-06 20:00:38.615456

"""

# revision identifiers, used by Alembic.
revision = '28883f040e44'
down_revision = '54ed57d1575b'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.alter_column('PGWOrderStatus', 'pgw_sub_service_id',
                    nullable=False, existing_nullable=True, existing_type=sa.Unicode(length=50))


def downgrade():
    op.alter_column('PGWOrderStatus', 'pgw_sub_service_id',
                    nullable=True, existing_nullable=False, existing_type=sa.Unicode(length=50))
