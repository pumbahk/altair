"""alter table OrganizationSetting add lot_asid

Revision ID: 482f7ef338d1
Revises: 30afb058c47
Create Date: 2015-01-19 14:45:34.139532

"""

# revision identifiers, used by Alembic.
revision = '482f7ef338d1'
down_revision = '30afb058c47'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('OrganizationSetting', sa.Column('lot_asid', sa.String(length=255), nullable=True))
    op.execute("UPDATE OrganizationSetting SET lot_asid='NTRhY2FkMWNlOWM2M7PaxbelwaWxpcOlyA' WHERE id = 42")

def downgrade():
    op.drop_column('OrganizationSetting', 'lot_asid')
