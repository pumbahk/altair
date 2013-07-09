"""change_issue_column_type

Revision ID: 20b9eeb7686
Revises: 20ed005e38e
Create Date: 2013-07-09 15:18:02.622915

"""

# revision identifiers, used by Alembic.
revision = '20b9eeb7686'
down_revision = '20ed005e38e'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.alter_column('AccessToken', 'issue',
        type_=sa.DateTime(),
        existing_nullable=True,
        )

def downgrade():
    op.alter_column('AccessToken', 'issue',
        type_=sa.Integer(),
        existing_nullable=True,
        )
