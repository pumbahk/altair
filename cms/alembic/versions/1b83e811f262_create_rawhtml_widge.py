"""create rawhtml widget

Revision ID: 1b83e811f262
Revises: 53c4dee5c464
Create Date: 2012-07-14 21:22:09.628980

"""

# revision identifiers, used by Alembic.
revision = '1b83e811f262'
down_revision = '53c4dee5c464'

from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table('widget_rawhtml',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('text', sa.UnicodeText(), nullable=True),
                    sa.ForeignKeyConstraint(['id'], ['widget.id'], name="fk_widget_rawhtml_id_to_widget_id"),
                    sa.PrimaryKeyConstraint('id')
                    )
    

def downgrade():
    op.drop_table("widget_rawhtml")
