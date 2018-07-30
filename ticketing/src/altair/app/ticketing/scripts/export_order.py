#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os
import logging
import locale
import subprocess
import csv
import hashlib
import sys
import traceback

from argparse import ArgumentParser
from collections import OrderedDict
from Crypto.Cipher import AES
from Crypto import Random
from datetime import datetime, timedelta
from pyramid.paster import bootstrap
from sqlalchemy import and_
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from altair.app.ticketing.core.models import (
    Organization,
    Performance,
    PaymentDeliveryMethodPair,
    PaymentMethod,
    ShippingAddress
)
from altair.app.ticketing.orders.models import (
    Order,
    OrderAttribute
)
from altair.app.ticketing.cart.models import CartSetting
from altair.sqlahelper import get_db_session

# Batch Status
(BATCH_SUCCESS, BATCH_FAILURE) = (0, 1)

# Logger Setting
charset = locale.getpreferredencoding()
if charset == 'US-ASCII':
    charset = 'utf-8'

logger = logging.getLogger(__name__)
output = sys.stdout

# Subcommand List
(GENERATE_KEY, ENCRYPT, DECRYPT) = ('generate_key', 'encrypt', 'decrypt')

# Encode
CSV_FILE_ENCODE = 'utf-8'
SETTING_ASCII_ENCODE = "unicode-escape"

DATE_FORMAT = '%Y-%m-%d'

TARGET_CART_SETTING = 'fc'
# For STG TEST
# TARGET_CART_SETTING = 'standard'

# Key list on ini file
SETTING_KEY = {
    'EVENT_IDS': '{}.export.order.event.ids',
    'ENC_BASE_KEY_FORMAT': '{}.export.order.enc.base.key',
    'ENC_KEY_FILE_PATH_FORMAT': '{}.export.order.enc.key.file.path',
    'ENC_IV_FILE_PATH_FORMAT': '{}.export.order.enc.iv.file.path',
    'ENC_SALT_FILE_PATH_FORMAT': '{}.export.order.enc.salt.file.path',
    'WORK_DIR': '{}.export.order.work.dir',
    'CVS_TMP_FILE_PATH_FORMAT': '{}.export.order.cvs.tmp.file.path',
    'CVS_ENC_FILE_PATH_FORMAT': '{}.export.order.cvs.enc.file.path',
    'CVS_DEC_FILE_PATH_FORMAT': '{}.export.order.cvs.dec.file.path',
    'S3_BUCKET_NAME_FORMAT': '{}.export.order.s3.bucket.name',
    'S3_UPLOAD_PATH_FORMAT': '{}.export.order.s3.upload.path',
    'AWS_ACCESS_KEY': 's3.access_key',
    'AWS_SECRET': 's3.secret_key'
}

# Column list. Key is db label. Value is column name of csv.
COLUMN = OrderedDict([
    ('performanc_id', '公演ID'),
    ('performance_name', '公演'),
    ('order_no', '予約番号'),
    ('first_name', '配送先姓'),
    ('last_name', '配送先名'),
    ('first_name_kana', '配送先姓(カナ)'),
    ('last_name_kana', '配送先名(カナ)'),
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

COLUMN_ATTRIBUTE_KEY_PREFIX = '追加情報(Key)'
COLUMN_ATTRIBUTE_VALUE_PREFIX = '追加情報(Value)'
CMD_SED_ATTRIBUTE_KEY = "sed -i -e 's/追加情報\(Key\)\d{1,},/追加情報\(Key\)/g' "
CMD_SED_ATTRIBUTE_VALUE = "sed -i -e 's/追加情報\(Value\)\d{1,},/追加情報\(Value\)/g' "


class InValidArgumentException(Exception):
    """Exception for argument validation"""
    pass


def message(msg, auxiliary=False):
    """Message with logger"""
    logger.log(auxiliary and logging.DEBUG or logging.INFO, msg)
    pad = '  ' if auxiliary else ''
    print >>output, (pad + msg).encode(charset)


# Util
def get_request(config):
    """Get request from config"""
    env = bootstrap(config)
    request = env['request']
    return request


def get_setting_value(settings, key, default=None):
    """Get setting value on ini file"""
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


# File I/O
def write_csv(out_filename, csv_data, max_attribute_count, mode):
    """Write csv to file with csv_data"""
    with open(out_filename, mode) as f:

        fieldnames = []
        for key, value in COLUMN.items():
            fieldnames.append(value.encode(CSV_FILE_ENCODE))

        for i in range(max_attribute_count):
            fieldnames.append(COLUMN_ATTRIBUTE_KEY_PREFIX + i)
            fieldnames.append(COLUMN_ATTRIBUTE_VALUE_PREFIX + i)

        writer = csv.DictWriter(f, fieldnames, extrasaction='ignore')
        writer.writeheader()
        for data in csv_data:
            writer.writerow(data)


def execute_sed_with_subprocess(command_prefix, filename):
    """Execute command on subprocess"""
    command = command_prefix + filename
    result = subprocess.call(command, shell=True)
    if result != 0:
        raise ValueError('Cannot find csv file. So please confirm. csv_filename:{}'.format(filename))


def sed_csv_attribute_column(csv_filename):
    """Sed column name which is attribute name and value"""
    execute_sed_with_subprocess(CMD_SED_ATTRIBUTE_KEY, csv_filename)
    execute_sed_with_subprocess(CMD_SED_ATTRIBUTE_VALUE, csv_filename)


def read_file(in_filename, mode):
    """Read file to data"""
    with open(in_filename, mode) as f:
        return f.read()


def write_file(out_filename, data, mode):
    """Write data to file"""
    with open(out_filename, mode) as f:
        f.write(data)


# Upload/Download S3
def upload_file_to_s3(filename,
                      bucket_name,
                      upload_path,
                      aws_access_key,
                      aws_secret,
                      dry_run=True):

    if dry_run:
        message('filename:' + filename)
        message('bucket_name:' + bucket_name)
        message('upload_path:' + upload_path)
        message('aws_access_key:' + aws_access_key)
        message('aws_secret:' + aws_secret)
    else:
        s3 = S3Connection(aws_access_key, aws_secret)
        bucket = s3.get_bucket(bucket_name)
        k = Key(bucket)
        k.key = upload_path
        k.set_contents_from_filename(filename)


# Clean up
def clean_up(filename):
    """Delete file"""
    os.remove(filename)
    message("Clean up data succeeded. filename: {}".format(filename))


# DAO
def fetch_order_data(session, organization_id, event_id_list, start_at, end_at):
    """Fetch order data from database"""
    query = session.query(
        Order.id.label('order_id'),
        Order.performance_id.label('performance_id'),
        Performance.name.label('performance_name'),
        Order.order_no.label('order_no'),
        ShippingAddress.first_name.label('first_name'),
        ShippingAddress.last_name.label('last_name'),
        ShippingAddress.first_name_kana.label('first_name_kana'),
        ShippingAddress.last_name_kana.label('last_name_kana'),
        ShippingAddress.sex.label('sex'),
        ShippingAddress.tel_1.label('tel_1'),
        ShippingAddress.email_1.label('email_1'),
        ShippingAddress.zip.label('zip'),
        ShippingAddress.country.label('country'),
        ShippingAddress.prefecture.label('prefecture'),
        ShippingAddress.city.label('city'),
        ShippingAddress.address_1.label('address_1'),
        ShippingAddress.address_2.label('address_2'),
        PaymentMethod.payment_plugin_id.label('payment_plugin_id')) \
        .join(Performance, Performance.id == Order.performance_id) \
        .join(PaymentDeliveryMethodPair, PaymentDeliveryMethodPair.id == Order.payment_delivery_method_pair_id) \
        .join(PaymentMethod, PaymentMethod.id == PaymentDeliveryMethodPair.payment_method_id) \
        .join(CartSetting, CartSetting.id == Order.cart_setting_id) \
        .join(ShippingAddress, ShippingAddress.id == Order.shipping_address_id) \
        .filter(Order.organization_id == organization_id) \
        .filter(Order.user_id.isnot(None)) \
        .filter(Order.canceled_at.is_(None)) \
        .filter(Order.refund_id.is_(None)) \
        .filter(and_(start_at <= Order.paid_at, Order.paid_at <= end_at)) \
        .filter(Performance.event_id.in_(event_id_list)) \
        .filter(ShippingAddress.deleted_at.is_(None)) \
        .filter(CartSetting.type == TARGET_CART_SETTING)

    return query.all()


def fetch_order_attributes(session, order_id):
    """Fetch order attributes data with order id"""
    query = session.query(OrderAttribute) \
        .filter(OrderAttribute.order_id == order_id)
    return query.all()


def fetch_organization_id(request, organization_code):
    """Fetch organization id from database with organization code"""
    session = get_db_session(request, name='slave')
    result = session.query(Organization) \
        .filter(Organization.code == organization_code).first()
    return result.id


# Regarding to CSV
def create_csv_data(results):
    """Create csv data to create csv file"""
    csv_data = []
    for result in results:
        result_dic = result.__dict__
        del result_dic['_labels']
        dic = {}
        for column, name in COLUMN.items():
            value = result_dic.get(column)
            if type(value) is unicode:
                value = value.encode(CSV_FILE_ENCODE)
            dic[name.encode(CSV_FILE_ENCODE)] = value

        csv_data.append(dic)

    return csv_data


# AES Operation
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


def encrypt_aes(key, iv, salt, in_filename, out_filename):
    """Encrypt file. Output file is binary file."""
    with open(in_filename, 'rb') as in_file:

        with open(out_filename, 'wb') as out_file:

            block_size = AES.block_size
            cipher = AES.new(key, AES.MODE_CBC, iv)
            out_file.write(salt)
            finished = False
            data_bytes = in_file.read()

            while not finished:
                chunk = data_bytes[:(1024 * block_size)]
                data_bytes = data_bytes[(1024 * block_size):]
                if len(chunk) == 0 or len(chunk) % block_size != 0:
                    padding_length = (block_size - len(chunk) % block_size) or block_size
                    chunk += padding_length * str.encode(chr(padding_length))
                    finished = True
                out_file.write(cipher.encrypt(chunk))


def decrypt_aes(key, iv, in_filename):
    """Decrypt file. Output file is string file."""

    with open(in_filename, 'rb') as in_file:
        block_size = AES.block_size
        in_file.read(block_size)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        next_chunk = b''
        finished = False
        data_bytes = b''
        while not finished:
            chunk = next_chunk
            next_chunk = cipher.decrypt(in_file.read(1024 * block_size))
            if len(chunk) == 0 and len(next_chunk) == 0:
                raise ValueError('File is empty')

            if len(next_chunk) == 0:
                finished = True
            data_bytes += chunk
        return data_bytes


def get_crypt_hash_key(filename):
    """Get binary data"""
    return read_file(filename, 'rb')


# Get Param from arguments
def get_target_date(args):
    """Get target_date value from args. If target_date is none, it set default date"""
    target_date = args.target_date
    if target_date is None:
        target_date = (datetime.now() - timedelta(days=1)).strftime(DATE_FORMAT)
    else:
        try:
            datetime.strptime(target_date, DATE_FORMAT)
        except ValueError:
            error_message = 'The target_date argument format is wrong. format: {}, target_date: {}'\
                .format(DATE_FORMAT, target_date)
            raise InValidArgumentException(error_message)
    return target_date


def get_organization_id(request, organization_code):
    """Get organization id. If it is none, this raise InValidArgumentException."""
    if organization_code is None:
        raise InValidArgumentException('Organization code is empty. So please input it')

    organization_id = fetch_organization_id(request, organization_code)
    if organization_id is None:
        raise InValidArgumentException('Not found organization on database')
    return organization_id


def get_params_on_generate_key_task(args):
    """Get need params from args for generate_key sub command."""
    request = get_request(args.config)
    settings = request.registry.settings
    organization_code = args.organization_code.lower()

    # check whether organization code is valid or not
    get_organization_id(request, organization_code)

    # get setting value
    base_key = get_setting_value(settings, SETTING_KEY['ENC_BASE_KEY_FORMAT'].format(organization_code))
    enc_key_filename = get_setting_value(settings, SETTING_KEY['ENC_KEY_FILE_PATH_FORMAT'].format(organization_code))
    enc_iv_filename = get_setting_value(settings, SETTING_KEY['ENC_IV_FILE_PATH_FORMAT'].format(organization_code))
    enc_salt_filename = get_setting_value(settings, SETTING_KEY['ENC_SALT_FILE_PATH_FORMAT'].format(organization_code))
    return base_key, enc_key_filename, enc_iv_filename, enc_salt_filename


def get_params_on_encrypt_task(args):
    """Get need params from args for encrypt sub command."""
    config = args.config
    request = get_request(config)
    settings = request.registry.settings

    organization_code = args.organization_code.lower()
    organization_id = get_organization_id(request, organization_code)
    target_date = get_target_date(args)
    dry_run = args.dry_run

    event_id_list = get_setting_value(settings, SETTING_KEY['EVENT_IDS'].format(organization_code), '').split(',')

    enc_key_filename = get_setting_value(settings, SETTING_KEY['ENC_KEY_FILE_PATH_FORMAT'].format(organization_code))
    enc_iv_filename = get_setting_value(settings, SETTING_KEY['ENC_IV_FILE_PATH_FORMAT'].format(organization_code))
    enc_salt_filename = get_setting_value(settings, SETTING_KEY['ENC_SALT_FILE_PATH_FORMAT'].format(organization_code))

    work_dir = get_setting_value(settings, SETTING_KEY['WORK_DIR'].format(organization_code))
    tmp_file_path = work_dir + get_setting_value(settings, SETTING_KEY['CVS_TMP_FILE_PATH_FORMAT'].format(organization_code))
    enc_filename = work_dir + get_setting_value(settings, SETTING_KEY['CVS_ENC_FILE_PATH_FORMAT'].format(organization_code))

    s3_bucket_name = get_setting_value(settings, SETTING_KEY['S3_BUCKET_NAME_FORMAT'].format(organization_code))
    s3_upload_path = get_setting_value(settings, SETTING_KEY['S3_UPLOAD_PATH_FORMAT'].format(organization_code))
    aws_access_key = get_setting_value(settings, SETTING_KEY['AWS_ACCESS_KEY'].format(organization_code))
    aws_secret = get_setting_value(settings, SETTING_KEY['AWS_SECRET'].format(organization_code))

    return (request,
            config,
            organization_id,
            event_id_list,
            target_date,
            tmp_file_path,
            enc_key_filename,
            enc_iv_filename,
            enc_salt_filename,
            work_dir,
            enc_filename,
            s3_bucket_name,
            s3_upload_path,
            aws_access_key,
            aws_secret,
            dry_run)


def get_args_on_decrypt_task(args):
    """Get need params from args for decrypt sub command."""
    config = args.config
    request = get_request(config)
    settings = request.registry.settings

    organization_code = args.organization_code.lower()
    organization_id = get_organization_id(request, organization_code)

    enc_key_filename = get_setting_value(settings, SETTING_KEY['ENC_KEY_FILE_PATH_FORMAT'].format(organization_code))
    enc_iv_filename = get_setting_value(settings, SETTING_KEY['ENC_IV_FILE_PATH_FORMAT'].format(organization_code))

    work_dir = get_setting_value(settings, SETTING_KEY['WORK_DIR'].format(organization_code))
    enc_filename = work_dir + get_setting_value(settings, SETTING_KEY['CVS_ENC_FILE_PATH_FORMAT'].format(organization_code))
    dec_filename = work_dir + get_setting_value(settings, SETTING_KEY['CVS_DEC_FILE_PATH_FORMAT'].format(organization_code))

    return (config,
            organization_id,
            enc_key_filename,
            enc_iv_filename,
            enc_filename,
            dec_filename)


# Sub command
def generate_key_task(args):
    """The generate_key sub command"""
    message('Start generate_key')
    (base_key, enc_key_filename, enc_iv_filename, enc_salt_filename) = get_params_on_generate_key_task(args)
    key_length = 32
    encoded_key = str.encode(base_key)
    block_size = AES.block_size
    salt = Random.new().read(block_size)
    crypt_hash_key, i_v = derive_key_and_iv(encoded_key, salt, key_length, block_size)
    write_file(enc_key_filename, bytearray(crypt_hash_key), 'wb')
    write_file(enc_iv_filename, bytearray(i_v), 'wb')
    write_file(enc_salt_filename, bytearray(salt), 'wb')
    message('Finish generate_key')


def encrypt_task(args):
    """The encrypt sub command"""
    message('Start encrypt')
    (
        request,
        config,
        organization_id,
        event_id_list,
        target_date,
        tmp_file_path,
        enc_key_filename,
        enc_iv_filename,
        enc_salt_filename,
        work_dir,
        enc_filename,
        s3_bucket_name,
        s3_upload_path,
        aws_access_key,
        aws_secret,
        dry_run
    ) = get_params_on_encrypt_task(args)

    if not os.path.isdir(work_dir):
        os.makedirs(work_dir)

    start_at = target_date + ' 00:00:00'
    end_at = target_date + ' 23:59:59'

    # Data fetch and decoration
    message('Fetch database data from {} to {}.'.format(start_at, end_at))
    session = get_db_session(request, name='slave')

    if len(event_id_list) > 0:
        results = fetch_order_data(session, organization_id, event_id_list, start_at, end_at)
    else:
        results = []

    if len(results) == 0:
        message('No target.')

    max_attribute_count = 0
    for result in results:
        order_id = result.order_id
        order_attributes = fetch_order_attributes(session, order_id)
        attribute_count = len(order_attributes)
        if attribute_count == 0:
            continue

        if max_attribute_count < attribute_count:
            max_attribute_count = attribute_count

        for index, attribute in enumerate(order_attributes):
            csv_column = COLUMN_ATTRIBUTE_KEY_PREFIX + index
            csv_value = COLUMN_ATTRIBUTE_VALUE_PREFIX + index
            result[csv_column] = attribute.name
            result[csv_value] = attribute.value

    # Create cvs file
    cvs_data = create_csv_data(results)
    write_csv(tmp_file_path, cvs_data, max_attribute_count, 'w')
    sed_csv_attribute_column(tmp_file_path)
    crypt_hash_key = get_crypt_hash_key(enc_key_filename)
    iv = get_crypt_hash_key(enc_iv_filename)
    salt = get_crypt_hash_key(enc_salt_filename)
    encrypt_aes(crypt_hash_key, iv, salt, tmp_file_path, enc_filename)
    upload_file_to_s3(enc_filename,
                      s3_bucket_name,
                      s3_upload_path,
                      aws_access_key,
                      aws_secret,
                      dry_run=dry_run)

    # Clean up temporary files
    clean_up(tmp_file_path)
    clean_up(tmp_file_path + '-e')
    message('Finish encrypt')


def decrypt_task(args):
    """The decrypt sub command"""
    message('Start decrypt')
    (
        config,
        organization_id,
        enc_key_filename,
        enc_iv_filename,
        enc_filename,
        dec_filename
    ) = get_args_on_decrypt_task(args)
    crypt_hash_key = get_crypt_hash_key(enc_key_filename)
    iv = get_crypt_hash_key(enc_iv_filename)
    data = decrypt_aes(crypt_hash_key, iv, enc_filename)
    write_file(dec_filename, data, 'w')
    message('Finish decrypt')


def main():
    # Load argument of batch
    parser = ArgumentParser()
    subparsers = parser.add_subparsers(help='sub-command help')

    # generate_key sub command
    generate_key_parser = subparsers.add_parser(GENERATE_KEY, help='a help')
    generate_key_parser.add_argument('--config', type=str, required=True,
                                     help='Config file name')
    generate_key_parser.add_argument('--organization_code', type=str, required=True,
                                     help='Organization Code')
    generate_key_parser.set_defaults(handler=generate_key_task)

    # encrypt sub command
    encrypt_parser = subparsers.add_parser(ENCRYPT, help='a help')
    encrypt_parser.add_argument('--config', type=str, required=True,
                                help='Config file name')
    encrypt_parser.add_argument('--organization_code', type=str, required=True,
                                help='Organization Code')
    encrypt_parser.add_argument('--dry_run', action='store_true', help='Dry run flag')
    encrypt_parser.add_argument('--target_date', type=str, required=False,
                                help='Target date. Format: YYYY-mm-dd')
    encrypt_parser.set_defaults(handler=encrypt_task)

    # decrypt sub command
    decrypt_parser = subparsers.add_parser(DECRYPT, help='a help')
    decrypt_parser.add_argument('--config', type=str, required=True,
                                help='Config file name')
    decrypt_parser.add_argument('--organization_code', type=str, required=True,
                                help='Organization Code')
    decrypt_parser.set_defaults(handler=decrypt_task)

    args = parser.parse_args()

    if hasattr(args, 'handler'):
        try:
            args.handler(args)
        except InValidArgumentException as ie:
            message(ie.message)
            return BATCH_FAILURE
        except ValueError as ve:
            message(ve.message)
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
