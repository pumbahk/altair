"""Performance.redirect_url_[pc,mobile]

Revision ID: 85564a50acf
Revises: 429ba0125909
Create Date: 2012-12-27 20:11:40.057268

"""

# revision identifiers, used by Alembic.
revision = '85564a50acf'
down_revision = '429ba0125909'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('Performance', sa.Column('redirect_url_pc', sa.String(1024)))
    op.add_column('Performance', sa.Column('redirect_url_mobile', sa.String(1024)))

def downgrade():
    op.drop_column('Performance', 'redirect_url_mobile')
    op.drop_column('Performance', 'redirect_url_pc')
