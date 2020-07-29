"""alter talbe ExternalSerialCodeSetting modify product_item_id

Revision ID: 3f70b09bd2bb
Revises: 400b8d1e91cd
Create Date: 2020-07-29 14:24:32.718646

"""

# revision identifiers, used by Alembic.
revision = '3f70b09bd2bb'
down_revision = '400b8d1e91cd'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.execute('ALTER TABLE ExternalSerialCodeSetting MODIFY COLUMN product_item_id BIGINT;')


def downgrade():
    op.drop_constraint('ExternalSerialCodeSetting_ibfk_1', 'ExternalSerialCodeSetting', type_='foreignkey')
    op.execute('ALTER TABLE ExternalSerialCodeSetting MODIFY COLUMN product_item_id BIGINT NOT NULL;')
    op.create_foreign_key(u'ExternalSerialCodeSetting_ibfk_1', u'ExternalSerialCodeSetting', u'ProductItem',
                          ['product_item_id'], ['id'])
