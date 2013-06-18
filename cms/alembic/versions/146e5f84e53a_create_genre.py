"""create genre

Revision ID: 146e5f84e53a
Revises: 3624a7d0cf20
Create Date: 2013-02-12 23:26:04.966129

"""

# revision identifiers, used by Alembic.
revision = '146e5f84e53a'
down_revision = '3624a7d0cf21'

from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table('genre',
                    sa.Column('organization_id', sa.Integer(), nullable=True),
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('label', sa.Unicode(length=255), nullable=True),
                    sa.Column('name', sa.String(length=255), nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('genre_path',
                    sa.Column('genre_id', sa.Integer(), nullable=False),
                    sa.Column('next_id', sa.Integer(), nullable=False),
                    sa.Column('hop', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(['genre_id'], ['genre.id'], ),
                    sa.ForeignKeyConstraint(['next_id'], ['genre.id'], ),
                    sa.PrimaryKeyConstraint('genre_id', 'next_id'),
                    sa.UniqueConstraint('genre_id','next_id')
                    )

def downgrade():
    op.drop_table('genre_path')
    op.drop_table('genre')
