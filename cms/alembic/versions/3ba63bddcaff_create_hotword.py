"""create hotword

Revision ID: 3ba63bddcaff
Revises: 1c6d20cb9391
Create Date: 2012-05-24 19:00:43.060612

"""

# revision identifiers, used by Alembic.
revision = '3ba63bddcaff'
down_revision = '1c6d20cb9391'

from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table('hotword',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('tag_id', sa.Integer(), nullable=True),
                    sa.Column('name', sa.Unicode(length=255), nullable=True),
                    sa.Column('orderno', sa.Integer(), nullable=True),
                    sa.Column('enablep', sa.Boolean(), nullable=True),
                    sa.Column('term_begin', sa.DateTime(), nullable=True),
                    sa.Column('term_end', sa.DateTime(), nullable=True),
                    sa.Column('created_at', sa.DateTime(), nullable=True),
                    sa.Column('updated_at', sa.DateTime(), nullable=True),
                    sa.Column('site_id', sa.Integer(), nullable=True),
                    sa.CheckConstraint('TODO'),
                    sa.ForeignKeyConstraint(['site_id'], ['site.id'], ),
                    sa.ForeignKeyConstraint(['tag_id'], ['pagetag.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )

def downgrade():
    op.drop_table('hotword')

