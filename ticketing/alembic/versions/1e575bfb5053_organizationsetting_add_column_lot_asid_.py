"""OrganizationSetting add column lot_asid_smartphone, lot_asid_mobile

Revision ID: 1e575bfb5053
Revises: 3c18f69f5b9
Create Date: 2015-09-08 15:33:18.583736

"""

# revision identifiers, used by Alembic.
revision = '1e575bfb5053'
down_revision = '3c18f69f5b9'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('OrganizationSetting', sa.Column('lot_asid_smartphone', sa.String(length=255), nullable=True))
    op.add_column('OrganizationSetting', sa.Column('lot_asid_mobile', sa.String(length=255), nullable=True))
    op.execute("UPDATE OrganizationSetting SET lot_asid_smartphone='NTRhY2FkMWNlOWM2M7PaxbelwaWxpcOlyA' WHERE id = 42")
    op.execute("UPDATE OrganizationSetting SET lot_asid_mobile='NTRhY2FkMWNlOWM2M7PaxbelwaWxpcOlyA' WHERE id = 42")

def downgrade():
    op.drop_column('OrganizationSetting', 'lot_asid_smartphone')
    op.drop_column('OrganizationSetting', 'lot_asid_mobile')
