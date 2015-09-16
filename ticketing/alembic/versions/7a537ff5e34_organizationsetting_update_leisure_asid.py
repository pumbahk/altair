"""OrganizationSetting update leisure asid

Revision ID: 7a537ff5e34
Revises: 1e575bfb5053
Create Date: 2015-09-16 10:34:00.574149

"""

# revision identifiers, used by Alembic.
revision = '7a537ff5e34'
down_revision = '1e575bfb5053'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.execute("UPDATE OrganizationSetting SET asid='NTVmMGVlNjNjMDdhZLP0vLCy8bzSpcGlsaXDpciluaWobw' WHERE id = 57")
    op.execute("UPDATE OrganizationSetting SET asid_smartphone='NTVmMGVmMDJhYjU3MrP0vLCy8bzSpcGlsaXDpciluaWobw' WHERE id = 57")
    op.execute("UPDATE OrganizationSetting SET asid_mobile='NTVmMGVlZDJiMTdmNrP0vLCy8bzSpcGlsaXDpciluaWobw' WHERE id = 57")
    op.execute("UPDATE OrganizationSetting SET lot_asid='NTVmMGVmM2EyZDA0YrP0vLCy8bzSpcGlsaXDpciluaWobw' WHERE id = 57")
    op.execute("UPDATE OrganizationSetting SET lot_asid_smartphone='NTVmMGVmYjM0ZGQ1ObP0vLCy8bzSpcGlsaXDpciluaWobw' WHERE id = 57")
    op.execute("UPDATE OrganizationSetting SET lot_asid_mobile='NTVmMGVmNzY2ODEwMbP0vLCy8bzSpcGlsaXDpciluaWobw' WHERE id = 57")

def downgrade():
    op.execute("UPDATE OrganizationSetting SET asid=NULL WHERE id = 57")
    op.execute("UPDATE OrganizationSetting SET asid_smartphone=NULL WHERE id = 57")
    op.execute("UPDATE OrganizationSetting SET asid_mobile=NULL WHERE id = 57")
    op.execute("UPDATE OrganizationSetting SET lot_asid=NULL WHERE id = 57")
    op.execute("UPDATE OrganizationSetting SET lot_asid_smartphone=NULL WHERE id = 57")
    op.execute("UPDATE OrganizationSetting SET lot_asid_mobile=NULL WHERE id = 57")
