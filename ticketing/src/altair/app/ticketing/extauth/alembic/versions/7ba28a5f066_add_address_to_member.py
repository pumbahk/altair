"""add_address_to_member

Revision ID: 7ba28a5f066
Revises: 48499844046e
Create Date: 2016-02-05 13:13:21.315427

"""

# revision identifiers, used by Alembic.
revision = '7ba28a5f066'
down_revision = '48499844046e'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    # op.add_column('Member', sa.Column('email', sa.Unicode(255), nullable=True))
    # op.add_column('Member', sa.Column('given_name', sa.Unicode(255), nullable=True))
    # op.add_column('Member', sa.Column('family_name', sa.Unicode(255), nullable=True))
    # op.add_column('Member', sa.Column('given_name_kana', sa.Unicode(255), nullable=True))
    # op.add_column('Member', sa.Column('family_name_kana', sa.Unicode(255), nullable=True))
    # op.add_column('Member', sa.Column('birthday', sa.Date(), nullable=True))
    # op.add_column('Member', sa.Column('gender', sa.Integer, nullable=True))
    # op.add_column('Member', sa.Column('country', sa.Unicode(64), nullable=True))
    # op.add_column('Member', sa.Column('zip', sa.Unicode(32), nullable=True))
    # op.add_column('Member', sa.Column('prefecture', sa.Unicode(128), nullable=True))
    # op.add_column('Member', sa.Column('city', sa.Unicode(255), nullable=True))
    # op.add_column('Member', sa.Column('address_1', sa.Unicode(255), nullable=True))
    # op.add_column('Member', sa.Column('address_2', sa.Unicode(255), nullable=True))
    # op.add_column('Member', sa.Column('tel_1', sa.Unicode(32), nullable=True))
    # op.add_column('Member', sa.Column('tel_2', sa.Unicode(32), nullable=True))
    op.execute('''ALTER TABLE `Member`
ADD COLUMN `email` VARCHAR(255) NULL,
ADD COLUMN `given_name` VARCHAR(255) NULL,
ADD COLUMN `family_name` VARCHAR(255) NULL,
ADD COLUMN `given_name_kana` VARCHAR(255) NULL,
ADD COLUMN `family_name_kana` VARCHAR(255) NULL,
ADD COLUMN `birthday` DATE NULL,
ADD COLUMN `gender` INTEGER NULL,
ADD COLUMN `country` VARCHAR(64) NULL,
ADD COLUMN `zip` VARCHAR(32) NULL,
ADD COLUMN `prefecture` VARCHAR(128) NULL,
ADD COLUMN `city` VARCHAR(255) NULL,
ADD COLUMN `address_1` VARCHAR(255) NULL,
ADD COLUMN `address_2` VARCHAR(255) NULL,
ADD COLUMN `tel_1` VARCHAR(32) NULL,
ADD COLUMN `tel_2` VARCHAR(32) NULL;''')

def downgrade():
    # op.drop_column('Member', 'email')
    # op.drop_column('Member', 'given_name')
    # op.drop_column('Member', 'family_name')
    # op.drop_column('Member', 'given_name_kana')
    # op.drop_column('Member', 'family_name_kana')
    # op.drop_column('Member', 'birthday')
    # op.drop_column('Member', 'gender')
    # op.drop_column('Member', 'country')
    # op.drop_column('Member', 'zip')
    # op.drop_column('Member', 'prefecture')
    # op.drop_column('Member', 'city')
    # op.drop_column('Member', 'dropress_1')
    # op.drop_column('Member', 'dropress_2')
    # op.drop_column('Member', 'tel_1')
    # op.drop_column('Member', 'tel_2')
    op.execute('''ALTER TABLE `Member`
DROP COLUMN `email`,
DROP COLUMN `given_name`,
DROP COLUMN `family_name`,
DROP COLUMN `given_name_kana`,
DROP COLUMN `family_name_kana`,
DROP COLUMN `birthday`,
DROP COLUMN `gender`,
DROP COLUMN `country`,
DROP COLUMN `zip`,
DROP COLUMN `prefecture`,
DROP COLUMN `city`,
DROP COLUMN `address_1`,
DROP COLUMN `address_2`,
DROP COLUMN `tel_1`,
DROP COLUMN `tel_2`;''')
