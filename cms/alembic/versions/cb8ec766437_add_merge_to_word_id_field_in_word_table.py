"""Add merge_to_word_id field in word table

Revision ID: cb8ec766437
Revises: 5649c3858eb1
Create Date: 2017-02-15 10:52:03.445282

"""

# revision identifiers, used by Alembic.
revision = 'cb8ec766437'
down_revision = '5649c3858eb1'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('word', sa.Column('merge_to_word_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_word_merge_to_word_id', 'word', 'word', ['merge_to_word_id'], ['id'])

def downgrade():
    op.drop_constraint('fk_word_merge_to_word_id', 'word', type='foreignkey')
    op.drop_column('word', 'merge_to_word_id')
