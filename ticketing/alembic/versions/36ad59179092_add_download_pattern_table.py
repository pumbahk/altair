"""add_download_pattern_table

Revision ID: 36ad59179092
Revises: 3d11d457ae32
Create Date: 2016-12-06 15:32:20.235239

"""

# revision identifiers, used by Alembic.
revision = '36ad59179092'
down_revision = '3d11d457ae32'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.create_table('DownloadItemsPattern',
        sa.Column('id', Identifier(), nullable=False),
        sa.Column('organization_id', Identifier(), nullable=False),
        sa.Column('pattern_name', sa.Unicode(length=255), nullable=False),
        sa.Column('pattern_content', sa.Unicode(length=4095), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(),
                   nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(),
                   nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['organization_id'], ['Organization.id'],
                                 'downloaditemspattern_ibfk_1', ondelete='CASCADE'),
        sa.UniqueConstraint('organization_id', 'pattern_name', name='uix_1')
    )

def downgrade():
    op.drop_constraint('downloaditemspattern_ibfk_1', 'DownloadItemsPattern', type='foreignkey')
    op.drop_constraint('uix_1', 'DownloadItemsPattern', type='unique')
    op.drop_table('DownloadItemsPattern')
