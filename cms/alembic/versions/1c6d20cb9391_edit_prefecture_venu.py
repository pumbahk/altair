"""edit prefecture venue

Revision ID: 1c6d20cb9391
Revises: 2cbf959ed694
Create Date: 2012-05-23 20:17:44.187547

"""

# revision identifiers, used by Alembic.
revision = '1c6d20cb9391'
down_revision = '2cbf959ed694'

from alembic import op
import sqlalchemy as sa

##:IMPORT_SYMBOL
import pkg_resources
def import_symbol(symbol):
    return pkg_resources.EntryPoint.parse("x=%s" % symbol).load(False)

def upgrade():
    enums = import_symbol("altaircms.seeds.prefecture:PREFECTURE_ENUMS")
    op.add_column("performance", sa.Column("prefecture", sa.Enum(*enums), nullable=True))

def downgrade():
    op.drop_column("performance", "prefecture")

