"""resize account_type, account_number, account_holder_name of ResaleRequest

Revision ID: 3cd361e34c44
Revises: 42fb5750b08a
Create Date: 2018-05-09 17:46:11.620268

"""

# revision identifiers, used by Alembic.
revision = '3cd361e34c44'
down_revision = '42fb5750b08a'

from alembic import op
from altair.aes_urlsafe import AESURLSafe

cryptor = AESURLSafe(key="AES_CRYPTOR_FOR_RESALE_REQUEST!!")


def upgrade():
    op.execute('alter table ResaleRequest modify column account_type varchar(255)')
    op.execute('alter table ResaleRequest modify column account_number varchar(255)')

    conn = op.get_bind()
    query = conn.execute("select id, account_type, account_number, account_holder_name from ResaleRequest;")
    data = query.fetchall()
    for item in data:
        encrypted_account_type = cryptor.encrypt(item[1])
        encrypted_account_number = cryptor.encrypt(item[2])
        encrypted_account_holder_name = cryptor.encrypt(item[3])
        op.execute(
            "update ResaleRequest set account_type = '{}', account_number = '{}', account_holder_name = '{}' where id = {}".format(
                encrypted_account_type,
                encrypted_account_number,
                encrypted_account_holder_name,
                item[0]
            ))



def downgrade():
    conn = op.get_bind()
    query = conn.execute("select id, account_type, account_number, account_holder_name from ResaleRequest;")
    data = query.fetchall()
    for item in data:
        decrypted_account_type = cryptor.decrypt(item[1].encode('utf-8')).encode('utf-8')
        decrypted_account_number = cryptor.decrypt(item[2].encode('utf-8')).encode('utf-8')
        decrypted_account_holder_name = cryptor.decrypt(item[3].encode('utf-8')).encode('utf-8')

        sql = "update ResaleRequest set account_type = '{}', account_number = '{}', account_holder_name = '{}' where id = {}".format(
            decrypted_account_type,
            decrypted_account_number,
            decrypted_account_holder_name,
            item[0]
        )
        op.execute(sql.decode('utf-8'))

    op.execute('alter table ResaleRequest modify column account_type varchar(64)')
    op.execute('alter table ResaleRequest modify column account_number varchar(44)')
