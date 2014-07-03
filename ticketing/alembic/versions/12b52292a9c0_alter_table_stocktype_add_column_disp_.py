"""alter table StockType add column disp_reports

Revision ID: 12b52292a9c0
Revises: 145a56bd800c
Create Date: 2014-07-02 13:57:12.029430

"""

# revision identifiers, used by Alembic.
revision = '12b52292a9c0'
down_revision = '145a56bd800c'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('StockType', sa.Column('disp_reports', sa.Boolean(), nullable=False,default=True, server_default=text('1')))

def downgrade():
    op.drop_column('StockType', 'disp_reports')
