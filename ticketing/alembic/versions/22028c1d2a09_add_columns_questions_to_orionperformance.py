"""add columns questions to orionperformance

Revision ID: 22028c1d2a09
Revises: 2e45c8b61b2d
Create Date: 2020-06-15 13:08:14.665754

"""

# revision identifiers, used by Alembic.
revision = '22028c1d2a09'
down_revision = '2e45c8b61b2d'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf
from sqlalchemy.dialects.mysql import MEDIUMTEXT

Identifier = sa.BigInteger


def upgrade():
    op.add_column('OrionPerformance', sa.Column('questions', MEDIUMTEXT(charset='utf8'), nullable=True, default=""))

def downgrade():
    op.drop_column('OrionPerformance', 'questions')
