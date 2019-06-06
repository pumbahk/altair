"""create_PGWMaskedCardDetail_table

Revision ID: 54ed57d1575b
Revises: 402f797572f4
Create Date: 2019-06-05 12:56:20.896119

"""

# revision identifiers, used by Alembic.
revision = '54ed57d1575b'
down_revision = '402f797572f4'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.create_table('PGWMaskedCardDetail',
                    sa.Column('id', Identifier(), nullable=False),
                    sa.Column('user_id', Identifier, nullable=False),
                    sa.Column('card_token', sa.Unicode(length=50), nullable=False),
                    sa.Column('card_iin', sa.SmallInteger, nullable=False),
                    sa.Column('card_last4digits', sa.SmallInteger, nullable=False),
                    sa.Column('card_expiration_month', sa.SmallInteger, nullable=False),
                    sa.Column('card_expiration_year', sa.SmallInteger, nullable=False),
                    sa.Column('card_brand_code', sa.Unicode(length=30), nullable=False),
                    sa.Column('created_at', sa.TIMESTAMP(),
                              server_default=sqlf.current_timestamp(), index=True, nullable=False),
                    sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
                    sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
                    sa.PrimaryKeyConstraint('id'),
                    sa.ForeignKeyConstraint(['user_id'], ['User.id'],
                                            name="PGWMaskedCardDetail_ibfk_1"),
                    sa.UniqueConstraint('user_id', name="ix_PGWMaskedCardDetail_user_id")
                    )


def downgrade():
    op.drop_table('PGWMaskedCardDetail')
