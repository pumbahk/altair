#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import logging
import locale
import random
import os
import csv
import struct
import hashlib
import sys
import StringIO
import codecs
import traceback


from collections import OrderedDict
from datetime import datetime
from Crypto.Cipher import AES
from Crypto import Random
from argparse import ArgumentParser
from altair.app.ticketing.orders.models import Order, Performance, PaymentDeliveryMethodPair, PaymentMethod, UserProfile, Organization
from altair.app.ticketing.cart.models import CartSetting
from pyramid.paster import bootstrap
from sqlalchemy import and_
from altair.sqlahelper import get_db_session
from sqlalchemy.dialects import mysql


# Batch Status
(BATCH_SUCCESS, BATCH_FAILURE) = (0, 1)

# Subcommand List
(GENERATE_KEY, ENCRYPT, DECRYPT) = ('generate_key', 'encrypt', 'decrypt')

CSV_FILE_ENCODE = 'utf-8'
SETTING_ASCII_ENCODE = "unicode-escape"

DATE_FORMAT = '%Y-%m-%d'

# TARGET_CART_SETTING = 'fc'
# For STG TEST
TARGET_CART_SETTING = 'standard'

CHUNK_SIZE = 24 * 1024

SETTING_KEY = {
    u'ENC_BASE_KEY_FORMAT': u'{}.export.order.enc.base.key',
    u'ENC_KEY_FILE_PATH_FORMAT': u'{}.export.order.enc.key.file.path',
    u'CVS_TMP_FILE_PATH_FORMAT': u'{}.export.order.cvs.tmp.file.path',
    u'CVS_FIELDNAMES_FORMAT': u'{}.export.order.cvs.fieldnames',
    u'CVS_ENC_FILE_PATH_FORMAT': u'{}.export.order.cvs.enc.file.path'
}

COLUMN = OrderedDict([
    ('performance_id', '公演ID'),
    ('performance_name', '公演'),
    ('order_no', '予約番号'),
    ('first_name', '姓'),
    ('last_name', '名'),
    ('first_name_kana', '姓(カナ)'),
    ('last_name_kana', '名(カナ)'),
    ('sex', '性別'),
    ('tel1', '電話番号1'),
    ('email1', 'メールアドレス1'),
    ('zip', '郵便番号'),
    ('country', '国'),
    ('prefecture', '都道府県'),
    ('city', '市区町村'),
    ('address1', '住所1'),
    ('address2', '住所2'),
    ('payment_method_id', '決済方法')
])

charset = locale.getpreferredencoding()
if charset == 'US-ASCII':
    charset = 'utf-8'

logger = logging.getLogger(__name__)

quiet = False
output = sys.stdout


class ObjectiveDictionary(dict):
    def __getattr__(self, name):
        if name in self:
            return self[name]
        else:
            raise AttributeError("No such attribute: " + name)

    def __setattr__(self, name, value):
        self[name] = value

    def __delattr__(self, name):
        if name in self:
            del self[name]
        else:
            raise AttributeError("No such attribute: " + name)


def set_quiet(q):
    global quiet, output
    if q:
        output = StringIO.StringIO()
    else:
        if quiet:
            print >>sys.stdout, output.getvalue()
            output.close()
        output = sys.stdout
    quiet = q


def message(msg, auxiliary=False):
    logger.log(auxiliary and logging.DEBUG or logging.INFO, msg)
    pad = '  ' if auxiliary else ''
    print >>output, (pad + msg).encode(charset)


class InValidArgumentException(Exception):
    pass


def write_csv(out_filename, csv_data, mode):
    with open(out_filename, mode) as f:

        fieldnames = []
        for key, value in COLUMN.items():
            print(key)
            fieldnames.append(value.encode(CSV_FILE_ENCODE))
        writer = csv.DictWriter(f, fieldnames, extrasaction='ignore')
        writer.writeheader()
        for data in csv_data:
            writer.writerow(data)


def write_file(out_filename, data, mode):
    with open(out_filename, mode) as f:
        bary = bytearray(data)
        f.write(bary)


def read_file(in_filename, mode):
    with open(in_filename, mode) as f:
        return f.read()


def derive_key_and_iv(password, salt, key_length, iv_length):
    """Auxilary function to generate key and iv for encryption/decryption
    Encryption/Decryption derived from:
    http://stackoverflow.com/questions/16761458/how-to-aes-encrypt-decrypt-files-using-python-pycrypto-in-an-openssl-compatible
    """
    key_and_iv = key_and_iv_chunk = b''
    while len(key_and_iv) < key_length + iv_length:
        key_and_iv_chunk = hashlib.sha256(key_and_iv_chunk + password + salt).digest()
        key_and_iv += key_and_iv_chunk
    return key_and_iv[:key_length], key_and_iv[key_length:key_length+iv_length]


def csv_to_bytes(csv_list):
    """Converts CSV list representation to bytes object"""
    csv_bytes = b''
    for row in csv_list:
        if row:
            for value in row:
                csv_bytes += str.encode("\"{}\",".format(value))
            csv_bytes = csv_bytes[:-1]
        csv_bytes += b"\r\n"
    return csv_bytes


def encrypt_aes(key, in_filename, out_filename):
    iv = ''.join(chr(random.randint(0, 8)) for i in range(16))
    encryptor = AES.new(key, AES.MODE_CBC, iv)
    filesize = os.path.getsize(in_filename)
    with open(in_filename, 'rb') as infile:
        with open(out_filename, 'wb') as outfile:
            outfile.write(struct.pack('<Q', filesize))
            outfile.write(iv)
            while True:
                chunk = infile.read(CHUNK_SIZE)
                if len(chunk) == 0:
                    break
                elif len(chunk) % 16 != 0:
                    chunk += ' ' * (16 - len(chunk) % 16)

                outfile.write(encryptor.encrypt(chunk))

    # with open(out_filename, 'wb') as out_file:
    #
    #     password = str.encode(password)
    #     block_size = AES.block_size
    #     salt = Random.new().read(block_size)# - len(b'Salted__'))
    #     key, i_v = derive_key_and_iv(password, salt, key_length, block_size)
    #     cipher = AES.new(key, AES.MODE_CBC, i_v)
    #     out_file.write(salt)#(b'Salted__' + salt)
    #     finished = False
    #     csv_bytes = csv_to_bytes(in_csv)
    #
    #     while not finished:
    #         chunk = csv_bytes[:(1024 * block_size)]
    #         csv_bytes = csv_bytes[(1024 * block_size):]
    #         if len(chunk) == 0 or len(chunk) % block_size != 0:
    #             padding_length = (block_size - len(chunk) % block_size) or block_size
    #             chunk += padding_length * str.encode(chr(padding_length))
    #             finished = True
    #         out_file.write(cipher.encrypt(chunk))


def decrypt_aes(key, in_filename, out_filename):
    if not out_filename:
        out_filename = os.path.splitext(in_filename)[0]

    with open(in_filename, 'rb') as infile:
        org_size = struct.unpack('<Q', infile.read(struct.calcsize('Q')))[0]
        iv = infile.read(16)
        decryptor = AES.new(key, AES.MODE_CBC, iv)

        with open(out_filename, 'wb') as outfile:
            while True:
                chunk = infile.read(CHUNK_SIZE)
                if len(chunk) == 0:
                    break
                outfile.write(decryptor.decrypt(chunk))
            outfile.truncate(org_size)


def fetch_order_data(request, organization_id, start_at, end_at):
    session = get_db_session(request, name='slave')
    query = session.query(
        Order.performance_id.label('performance_id'),
        Performance.name.label('performance_name'),
        Order.order_no.label('order_no'),
        UserProfile.first_name.label('first_name'),
        UserProfile.last_name.label('last_name'),
        UserProfile.first_name_kana.label('first_name_kana'),
        UserProfile.last_name_kana.label('last_name_kana'),
        UserProfile.sex.label('sex'),
        UserProfile.tel_1.label('tel_1'),
        UserProfile.email_1.label('email_1'),
        UserProfile.zip.label('zip'),
        UserProfile.country.label('country'),
        UserProfile.prefecture.label('prefecture'),
        UserProfile.city.label('city'),
        UserProfile.address_1.label('address_1'),
        UserProfile.address_2.label('address_2'),
        PaymentMethod.payment_plugin_id.label('payment_plugin_id')) \
        .join(Performance, Performance.id == Order.performance_id) \
        .join(PaymentDeliveryMethodPair, PaymentDeliveryMethodPair.id == Order.payment_delivery_method_pair_id) \
        .join(PaymentMethod, PaymentMethod.id == PaymentDeliveryMethodPair.payment_method_id) \
        .join(CartSetting, CartSetting.id == Order.cart_setting_id) \
        .join(UserProfile, UserProfile.user_id == Order.user_id) \
        .filter(Order.organization_id == organization_id) \
        .filter(Order.user_id.isnot(None)) \
        .filter(Order.canceled_at.is_(None)) \
        .filter(Order.refund_id.is_(None)) \
        .filter(and_(start_at <= Order.paid_at, Order.paid_at <= end_at)) \
        .filter(UserProfile.deleted_at.is_(None))\
        .filter(CartSetting.type == TARGET_CART_SETTING)

    message(str(query.statement.compile(dialect=mysql.dialect())))

    return query.all()


def fetch_organization_id(request, organization_code):
    session = get_db_session(request, name='slave')
    result = session.query(Organization) \
        .filter(Organization.code == organization_code).first()
    return result.id


def upload_file(filename):
    print("upload file to S3 {}".format(filename))


def create_csv_data(results):
    csv_data = []
    for result in results:
        result_dic = result.__dict__
        del result_dic['_labels']
        dic = {}
        for column, name in COLUMN.items():
            value = result_dic.get(column)
            if type(value) is unicode:
                value = value.encode(CSV_FILE_ENCODE)
            print(value)
            dic[name.encode(CSV_FILE_ENCODE)] = value

        csv_data.append(dic)
        message(str(csv_data))

    return csv_data


def get_crypt_hash_key(filename):
    return read_file(filename, 'rb')


def delete_old_data():
    print("Delete data succeeded")


# Get Param
def get_request(config):
    env = bootstrap(config)
    request = env['request']
    return request


def get_setting_value(settings, key, default=None):

    if key is None:
        raise InValidArgumentException('Setting key is none. key: {}'.format(key))

    value = settings.get(key)
    if value is None:
        if default is None:
            raise InValidArgumentException('Not found setting value. key: {}'.format(key))
        else:
            return default
    else:
        return value


def get_target_date(args):
    target_date = args.target_date
    if target_date is None:
        target_date = datetime.now().strftime(DATE_FORMAT)
    else:
        try:
            datetime.strptime(target_date, DATE_FORMAT)
        except ValueError:
            error_message = 'The target_date argument format is wrong. format: {}, target_date: {}'\
                .format(DATE_FORMAT, target_date)
            raise InValidArgumentException(error_message)
    return target_date


def get_organization_id(request, organization_code):
    if organization_code is None:
        raise InValidArgumentException('Organization code is empty. So please input it')

    organization_id = fetch_organization_id(request, organization_code)
    if organization_id is None:
        raise InValidArgumentException('Not found organization on database')
    return organization_id


def get_params_on_generate_key_task(args):

    request = get_request(args.config)
    settings = request.registry.settings
    organization_code = args.organization_code

    # check whether organization code is valid or not
    get_organization_id(request, organization_code)

    # get setting value
    base_key = get_setting_value(settings, SETTING_KEY['ENC_BASE_KEY_FORMAT'].format(organization_code))
    enc_key_filename = get_setting_value(settings, SETTING_KEY['ENC_KEY_FILE_PATH_FORMAT'].format(organization_code))

    return base_key, enc_key_filename


def get_params_on_encrypt_task(args):

    config = args.config
    request = get_request(config)
    settings = request.registry.settings

    organization_code = args.organization_code
    organization_id = get_organization_id(request, organization_code)

    tmp_file_path = get_setting_value(settings, SETTING_KEY['CVS_TMP_FILE_PATH_FORMAT'].format(organization_code))

    fieldnames_str = get_setting_value(settings, SETTING_KEY['CVS_FIELDNAMES_FORMAT'].format(organization_code))
    fieldnames_str = codecs.decode(fieldnames_str, SETTING_ASCII_ENCODE)
    fieldnames = fieldnames_str.split(',')

    enc_key_filename = get_setting_value(settings, SETTING_KEY['ENC_KEY_FILE_PATH_FORMAT'].format(organization_code))

    enc_filename_format = get_setting_value(settings, SETTING_KEY['CVS_ENC_FILE_PATH_FORMAT'].format(organization_code))
    target_date = get_target_date(args)
    enc_filename = enc_filename_format.format(target_date)

    return request, config, organization_id, target_date, tmp_file_path, fieldnames, enc_key_filename, enc_filename


def get_args_on_decrypt_task(args):

    config = args.config
    request = get_request(config)
    organization_code = args.organization_code
    organization_id = get_organization_id(request, organization_code)
    target_date = get_target_date(args)

    return config, organization_id, target_date


# Task
def generate_key_task(args):
    message("Start generate_key")
    (base_key, enc_key_filename) = get_params_on_generate_key_task(args)
    # key_length = 32
    crypt_hash_key = hashlib.sha256(base_key).digest()
    write_file(enc_key_filename, crypt_hash_key, 'wb')
    message("Finish generate_key")


def encrypt_task(args):

    message("Start encrypt")
    (
        request,
        config,
        organization_id,
        target_date,
        tmp_file_path,
        fieldnames,
        enc_key_filename,
        enc_filename

    ) = get_params_on_encrypt_task(args)

    start_at = target_date + ' 00:00:00'
    end_at = target_date + ' 23:59:59'

    # Create cvs file
    message('Fetch database data from {} to {}'.format(start_at, end_at))
    results = fetch_order_data(request, organization_id, start_at, end_at)

    if len(results) == 0:
        message('No target')

    cvs_data = create_csv_data(results)
    write_csv(tmp_file_path, cvs_data, 'w')
    crypt_hash_key = get_crypt_hash_key(enc_key_filename)
    encrypt_aes(crypt_hash_key, tmp_file_path, enc_filename)
    upload_file(enc_filename)
    delete_old_data()

    message("Finish encrypt")


def decrypt_task(args):
    message("Start decrypt")
    # (config, organization_id, target_date) = get_args_on_decrypt_task(args)
    # dec_filename = "test.tmp.csv"
    # crypt_hash_key = hashlib.sha256(CRYPT_ORG_KEY).digest()
    # decrypt_aes(crypt_hash_key, KEY_FILENAME, dec_filename)
    message("Finish decrypt")


def main():
    # Load argument of batch
    parser = ArgumentParser()
    subparsers = parser.add_subparsers(help='sub-command help')

    # generate_key task
    generate_key_parser = subparsers.add_parser(GENERATE_KEY, help='a help')
    generate_key_parser.add_argument('--config', type=str, required=True,
                                     help='Config file name')
    generate_key_parser.add_argument('--organization_code', type=str, required=True,
                                     help='Organization Code')
    generate_key_parser.set_defaults(handler=generate_key_task)

    # encrypt task
    encrypt_parser = subparsers.add_parser(ENCRYPT, help='a help')
    encrypt_parser.add_argument('--config', type=str, required=True,
                                help='Config file name')
    encrypt_parser.add_argument('--organization_code', type=str, required=True,
                                help='Organization Code')
    encrypt_parser.add_argument('--target_date', type=str, required=False,
                                help='Target date. Format: YYYY-mm-dd')
    encrypt_parser.set_defaults(handler=encrypt_task)

    # decrypt task
    decrypt_parser = subparsers.add_parser(DECRYPT, help='a help')
    decrypt_parser.add_argument('--config', type=str, required=True,
                                help='Config file name')
    decrypt_parser.add_argument('--organization_code', type=str, required=True,
                                help='Organization Code')
    decrypt_parser.add_argument('--target_date', type=str, required=False,
                                help='Target date. Format: YYYY-mm-dd')
    decrypt_parser.set_defaults(handler=decrypt_task)

    args = parser.parse_args()

    if hasattr(args, 'handler'):
        try:
            args.handler(args)
        except InValidArgumentException as ivae:
            message(ivae.message)
            return BATCH_FAILURE
        except Exception as e:
            message('Unexpected error. So please confirm the following traceback.')
            message(traceback.format_exc(e))
            return BATCH_FAILURE
    else:
        message('Wrong sub command. So please confirm your argument.')
        parser.print_help()
        return BATCH_FAILURE

    return BATCH_SUCCESS
