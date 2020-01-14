"""Add tables for skidata property.

Revision ID: 2c18d9d4fa27
Revises: 237be36dd727
Create Date: 2019-10-10 19:05:59.940582

"""

# revision identifiers, used by Alembic.
revision = '2c18d9d4fa27'
down_revision = '237be36dd727'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.create_table('SkidataProperty',
                    sa.Column('id', Identifier(), nullable=False, primary_key=True),
                    sa.Column('organization_id', Identifier(), nullable=False),
                    sa.Column('prop_type', sa.SmallInteger(), nullable=False),
                    sa.Column('name', sa.String(30), nullable=False),
                    sa.Column('value', sa.SmallInteger(), nullable=False),
                    sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
                    sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
                    sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
                    sa.ForeignKeyConstraint(['organization_id'], ['Organization.id'], 'SkidataProperty_ibfk_1',
                                            ondelete='CASCADE')
                    )
    op.create_table('SkidataPropertyEntry',
                    sa.Column('id', Identifier(), nullable=False, primary_key=True),
                    sa.Column('skidata_property_id', Identifier(), nullable=False),
                    sa.Column('related_id', Identifier(), nullable=False, index=True),
                    sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
                    sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
                    sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
                    sa.ForeignKeyConstraint(['skidata_property_id'], ['SkidataProperty.id'],
                                            'SkidataPropertyEntry_ibfk_1', ondelete='CASCADE')
                    )


def downgrade():
    op.drop_table('SkidataPropertyEntry')
    op.drop_table('SkidataProperty')
