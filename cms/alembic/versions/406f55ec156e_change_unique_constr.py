"""change unique constraint tag

Revision ID: 406f55ec156e
Revises: 146e5f84e53a
Create Date: 2013-02-12 23:48:07.121214

"""

# revision identifiers, used by Alembic.
revision = '406f55ec156e'
down_revision = '146e5f84e53a'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    op.drop_column('topiccoretag2topiccore', u'id')
    op.alter_column('topiccoretag2topiccore', 'tag_id',
               existing_type=mysql.INTEGER(display_width=11),
               nullable=False)
    op.alter_column('topiccoretag2topiccore', 'object_id',
               existing_type=mysql.INTEGER(display_width=11),
               nullable=False)
    op.drop_column('pagetag2page', u'id')
    op.alter_column('pagetag2page', 'tag_id',
               existing_type=mysql.INTEGER(display_width=11),
               nullable=False)
    op.alter_column('pagetag2page', 'object_id',
               existing_type=mysql.INTEGER(display_width=11),
               nullable=False)
    op.drop_column('assettag2asset', u'id')
    op.alter_column('assettag2asset', 'tag_id',
               existing_type=mysql.INTEGER(display_width=11),
               nullable=False)
    op.alter_column('assettag2asset', 'object_id',
               existing_type=mysql.INTEGER(display_width=11),
               nullable=False)
    op.drop_constraint("label", "assettag", type="unique")
    op.create_unique_constraint("label", "assettag", ["label", "organization_id", "publicp", "type"])
    op.drop_constraint("label", "pagetag", type="unique")
    op.create_unique_constraint("label", "pagetag", ["label", "organization_id", "publicp"])

def downgrade():
    op.alter_column('topiccoretag2topiccore', 'object_id',
               existing_type=mysql.INTEGER(display_width=11),
               nullable=True)
    op.alter_column('topiccoretag2topiccore', 'tag_id',
               existing_type=mysql.INTEGER(display_width=11),
               nullable=True)
    op.add_column('topiccoretag2topiccore', sa.Column(u'id', mysql.INTEGER(display_width=11), nullable=False))
    op.alter_column('assettag2asset', 'object_id',
               existing_type=mysql.INTEGER(display_width=11),
               nullable=True)
    op.alter_column('assettag2asset', 'tag_id',
               existing_type=mysql.INTEGER(display_width=11),
               nullable=True)
    op.add_column('assettag2asset', sa.Column(u'id', mysql.INTEGER(display_width=11), nullable=False))
    op.alter_column('pagetag2page', 'object_id',
               existing_type=mysql.INTEGER(display_width=11),
               nullable=True)
    op.alter_column('pagetag2page', 'tag_id',
               existing_type=mysql.INTEGER(display_width=11),
               nullable=True)
    op.add_column('pagetag2page', sa.Column(u'id', mysql.INTEGER(display_width=11), nullable=False))
    op.drop_constraint("label", "assettag", type="unique")
    op.create_unique_constraint("label", "assettag", ["label", "publicp", "type"])
    op.drop_constraint("label", "pagetag", type="unique")
    op.create_unique_constraint("label", "pagetag", ["label", "publicp"])
