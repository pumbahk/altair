"""add_foreign_key_on_augus_account

Revision ID: 3edeff1e01e0
Revises: 34ed7cee0c78
Create Date: 2018-06-19 13:50:53.271586

"""

# revision identifiers, used by Alembic.
revision = '3edeff1e01e0'
down_revision = '34ed7cee0c78'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.create_foreign_key(
        name='AugusAccount_ibfk_1',
        source='AugusAccount',
        referent='Account',
        local_cols=['account_id'],
        remote_cols=['id'],
        onupdate='CASCADE',
        ondelete='CASCADE'
    )


def downgrade():
    op.drop_constraint('AugusAccount_ibfk_1', 'AugusAccount', type_='foreignkey')
