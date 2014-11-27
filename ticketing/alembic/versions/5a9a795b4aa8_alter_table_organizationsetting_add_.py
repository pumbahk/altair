"""alter table OrganizationSetting add column asid

Revision ID: 5a9a795b4aa8
Revises: 41faffc1f5c7
Create Date: 2014-11-25 16:09:47.661237

"""

# revision identifiers, used by Alembic.
revision = '5a9a795b4aa8'
down_revision = '41faffc1f5c7'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('OrganizationSetting', sa.Column('asid', sa.String(length=255), nullable=True))
    op.add_column('OrganizationSetting', sa.Column('asid_mobile', sa.String(length=255), nullable=True))
    op.add_column('OrganizationSetting', sa.Column('asid_smartphone', sa.String(length=255), nullable=True))
    op.execute("UPDATE OrganizationSetting SET asid='NTI4MDU2ZDY2ZDI3ZLPaxbelwaWxpcOlyA' WHERE id = 24")
    op.execute("UPDATE OrganizationSetting SET asid_mobile='NTI2NzgxYTc1YjJhYbPaxbelwaWxpcOlyA' WHERE id = 24")
    op.execute("UPDATE OrganizationSetting SET asid_smartphone='NTI2NzgxMjJhMzRlM7PaxbelwaWxpcOlyA' WHERE id = 24")
    op.execute("UPDATE OrganizationSetting SET asid='NTQ3M2Q5ZjJiMGFiM7PaxbelwaWxpcOlyA' WHERE id = 42")
    op.execute("UPDATE OrganizationSetting SET asid_mobile='NTQ3M2RiNWNiNDUzZbPaxbelwaWxpcOlyA' WHERE id = 42")
    op.execute("UPDATE OrganizationSetting SET asid_smartphone='NTQ3M2RhZmRhMDFjMbPaxbelwaWxpcOlyA' WHERE id = 42")

def downgrade():
    op.drop_column('OrganizationSetting', 'asid')
    op.drop_column('OrganizationSetting', 'asid_mobile')
    op.drop_column('OrganizationSetting', 'asid_smartphone')
