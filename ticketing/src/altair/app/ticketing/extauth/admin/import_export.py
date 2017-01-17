# encoding: utf-8
import logging
import six
from collections import OrderedDict
from datetime import date, datetime, timedelta
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import sql
from dateutil.parser import parse as parsedate
from ..models import MemberSet, MemberKind, Member, Membership
from ..utils import generate_salt, digest_secret, DIGESTED_SECRET_LEN
from altair.tabular_data_io import lookup_reader, lookup_writer
from altair.tabular_data_io.impl.csv import CsvTabularDataReader, CsvTabularDataWriter

logger = logging.getLogger(__name__)


__all__ = [
    'TabularDataReader',
    'TabularDataWriter',
    'MemberDataParser',
    'MemberDataWriterAdapter',
    'MemberDataImporter',
    'MemberDataExporter',
    'MemberImportExportError',
    'MemberImportExportErrors',
    'japanese_columns',
    'gender_value_map',
    ] 


class _Unspecified(object):
    def __nonzero__(self):
        return False

    def __bool__(self):
        return False

Unspecified = _Unspecified()


japanese_columns = OrderedDict([
    (u'auth_identifier', u'ログインID'),
    (u'auth_secret', u'パスワード'),
    (u'name', u'氏名'),
    (u'membership_identifier', u'会員ID'),
    (u'member_set', u'会員種別'),
    (u'member_kind', u'会員区分'),
    (u'valid_since', u'開始日'),
    (u'expire_at', u'有効期限'),
    (u'email', u'メールアドレス'),
    (u'family_name', u'配送先姓'),
    (u'given_name', u'配送先名'),
    (u'family_name_kana', u'配送先姓(カナ)'),
    (u'given_name_kana', u'配送先名(カナ)'),
    (u'birthday', u'誕生日'),
    (u'gender', u'性別'),
    (u'country', u'国'),
    (u'zip', u'郵便番号'),
    (u'prefecture', u'都道府県'),
    (u'city', u'市区町村'),
    (u'address_1', u'住所1'),
    (u'address_2', u'住所2'),
    (u'tel_1', u'電話番号1'),
    (u'tel_2', u'電話番号2'),
    (u'deleted', u'削除フラグ'),
    ])

gender_value_map = {
    u'': Unspecified,
    u'-': None,
    u'未回答': 0,
    u'Unanswered': 0,
    u'N': 0,
    u'0': 0,
    u'男性': 1,
    u'男': 1,
    u'Male': 1,
    u'M': 1,
    u'1': 1,
    u'女性': 2,
    u'女': 2,
    u'Female': 2,
    u'F': 2,
    u'2': 2,
    }

ONE_SECOND = timedelta(seconds=1)

HASH_SIGNATURE = u'$hash$'

class TabularDataReader(object):
    def __init__(self, file, filename, column_name_map, type=None, csv_encoding='cp932'):
        reader_factory = lookup_reader(filename, type)
        options = {}
        if isinstance(reader_factory, CsvTabularDataReader):
            options['encoding'] = csv_encoding
        self.reader = reader_factory.open(file, **options)
        self.file = file
        self.filename = filename
        self.column_name_map = column_name_map
        self.line_num = 1
        columns = dict((v, k) for k, v in column_name_map.iteritems())
        header = []
        try:
            first_row = next(self.reader)
        except StopIteration:
            raise MemberImportExportError(u'ファイルの形式が正しくありません')
        self.line_num += 1
        for field in first_row:
            column_id = columns.get(field)
            if column_id is None:
                # 該当するカラムがない場合には、ヘッダに出現した内容をそのままキーとする
                column_id = field
            header.append(column_id)
        self.header = header

    def __iter__(self):
        for row in self.reader:
            yield {
                self.header[i]: v if v is not None else u''
                for i, v in enumerate(row)
                }
            self.line_num += 1

    @property
    def fieldnames(self):
        return self.reader.fieldnames


class TabularDataWriter(object):
    def __init__(self, file, header, column_names, type=None, csv_encoding='cp932'):
        writer_factory = lookup_writer(None, type)
        options = {}
        if isinstance(writer_factory, CsvTabularDataWriter):
            options['encoding'] = csv_encoding
            datetime_conversion_needed = True
        else:
            datetime_conversion_needed = False
        self.writer = writer_factory.open(file, **options)
        self.preferred_mime_type = writer_factory.preferred_mime_type
        self.file = file
        self.datetime_conversion_needed = datetime_conversion_needed
        self.line_num = 1
        self.column_names = column_names
        self.writer(header)
        self.line_num += 1

    @property
    def encoding(self):
        return self.writer.encoding

    def close(self):
        self.writer.close()

    def __call__(self, row):
        self.writer([row[k] for k in self.column_names])
        self.line_num += 1


class MemberImportExportErrorBase(Exception):
    pass


class MemberImportExportError(MemberImportExportErrorBase):
    def __init__(self, message, record_field_name_pairs, filename, line_num):
        return super(MemberImportExportError, self).__init__(
            message,
            record_field_name_pairs,
            filename,
            line_num
            )

    @classmethod
    def from_reader(cls, reader, record_field_names, message):
        return cls(
            message=message,
            record_field_name_pairs=[
                (k, reader.column_name_map[k])
                for k in record_field_names
                ],
            filename=reader.filename,
            line_num=reader.line_num
            )

    @property
    def message(self):
        return self.args[0]

    @property
    def record_field_name_pairs(self):
        return self.args[1]

    @property
    def filename(self):
        return self.args[2]

    @property
    def line_num(self):
        return self.args[3]


class MemberImportExportErrors(MemberImportExportErrorBase):
    def __init__(self, message, errors, num_records):
        super(MemberImportExportErrors, self).__init__(message, errors, num_records)

    @property
    def message(self):
        return self.args[0]

    @property
    def errors(self):
        return self.args[1]

    @property
    def num_records(self):
        return self.args[2]


class DictBuilder(object):
    def __init__(self, handleable_exceptions=()):
        self.errors = []
        self.result = {}
        self.handleable_exceptions = handleable_exceptions

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            if isinstance(exc_value, self.handleable_exceptions):
                self.errors.append(exc_value)
                return True
            else:
                raise

    def __setitem__(self, k, v):
        self.result[k] = v


def strip(v):
    return v.strip(u' \t　') if v is not None else None


def optional(reader, dict_, k, type_=six.text_type):
    if k not in dict_:
        return Unspecified
    v = dict_[k]
    if type_ is not None:
        if issubclass(type_, six.text_type):
            if isinstance(v, float):
                v = u'%g' % v
            else:
                v = type_(v)
        else:
            v = type_(v)
    if isinstance(v, six.text_type):
        v = strip(v)
    return v


def required(reader, dict_, k, type_=six.text_type, allow_blank=False):
    v = optional(reader, dict_, k, type_)
    if v is Unspecified or (not allow_blank and v == u''):
        raise MemberImportExportError.from_reader(
            reader, [k],
            u'「%s」は必須です' % reader.column_name_map[k]
            )
    return v


def validate_length(reader, dict_, k, min, max):
    errors = []
    v = dict_[k]
    if len(v) < min:
        errors.append(
            MemberImportExportError.from_reader(
                reader, [k],
                u'「%s」は%d文字以上にしてください' % (
                    reader.column_name_map[k],
                    min
                    )
                )
            )
    if len(v) > max:
        errors.append(
            MemberImportExportError.from_reader(
                reader, [k],
                u'「%s」は%d文字以下にしてください' % (
                    reader.column_name_map[k],
                    max
                    )
                )
            )
    return errors


def validate_term(reader, dict_, start_k, end_k):
    errors = []
    start = dict_[start_k]
    end = dict_[end_k]
    if start and end and start > end:
        errors.append(
            MemberImportExportError.from_reader(
                reader, [k],
                u'「%(start)s」は「%(end)s」より後でなければなりません' % dict(
                    start=reader.column_name_map[start_k],
                    end=reader.column_name_map[end_k]
                    )
                )
            )
    return errors


def parse_datetime(reader, dict_, k):
    if k not in dict_:
        return Unspecified
    raw_value = dict_.get(k)
    if raw_value is None:
        return Unspecified
    if isinstance(raw_value, date):
        return raw_value
    elif isinstance(raw_value, float):
        v = raw_value - 1.
        if v >= 61.: # THE LOTUS 1-2-3 bug
            v -= 1.
        days = int(v)
        return datetime(1900, 1, 1, 0, 0, 0) + timedelta(days=days, microseconds=86400000000.0 * (v - float(days)))
    elif not isinstance(raw_value, (str, six.text_type)):
        raw_value = six.text_type(raw_value)
    raw_value = strip(raw_value)
    if not raw_value:
        return Unspecified
    elif raw_value in (u'-', u'−'):
        return None
    return parsedate(raw_value)


def parse_date(reader, dict_, k):
    retval = parse_datetime(reader, dict_, k)
    if isinstance(retval, datetime):
        return retval.date()
    else:
        return retval


def parse_gender(reader, dict_, k):
    raw_value = dict_.get(k)
    if raw_value is None:
        return Unspecified
    if not isinstance(raw_value, (str, six.text_type)):
        raw_value = six.text_type(raw_value)
    raw_value = strip(raw_value)
    if not raw_value:
        return Unspecified
    try:
        retval = gender_value_map[raw_value]
    except KeyError:
        raise MemberImportExportError.from_reader(
            reader, [k],
            u'「%s」は正しい値ではありません' % raw_value
            )
    return retval


class MemberDataParser(object):
    def __init__(self, slave_session, organization_id):
        self.slave_session = slave_session
        self.organization_id = organization_id
        self.member_set_cache = {}
        self.members = {}

    def _resolve_member_set(self, reader, k, name):
        if name in self.member_set_cache:
            member_set = self.member_set_cache[name][0]
        else:
            member_set = None
            try:
                member_set = self.slave_session.query(MemberSet) \
                    .filter_by(organization_id=self.organization_id,
                               name=name) \
                    .one()
            except NoResultFound:
                pass
            self.member_set_cache[name] = (member_set, {})

        if member_set is None:
            raise MemberImportExportError.from_reader(
                reader, [k],
                u'「%s」は正しい会員種別名ではありません' % name
                )
        return member_set

    def _resolve_member_kind(self, reader, k, member_set, name):
        if not name:
            return None
        member_kinds = self.member_set_cache[member_set.name][1]
        if name in member_kinds:
            member_kind = member_kinds[name]
        else:
            member_kind = None
            try:
                member_kind = self.slave_session.query(MemberKind) \
                    .filter_by(member_set_id=member_set.id,
                               name=name) \
                    .one()
                member_kinds[member_kind.name] = member_kind
            except NoResultFound:
                pass
        if member_kind is None:
            raise MemberImportExportError.from_reader(
                reader, [k],
                u'「%s」は正しい会員区分名ではありません' % name
                )
        return member_kind

    def _resolve_membership(self, reader, member_id, member_kind, membership_identifier, valid_since, expire_at):
        membership_id = None
        try:
            q = self.slave_session.query(Membership.id) \
                .filter_by(member_id=member_id,
                           member_kind_id=member_kind.id)
            if membership_identifier is not Unspecified:
                q = q.filter_by(membership_identifier=membership_identifier)
            if valid_since is not Unspecified:
                q = q.filter_by(valid_since=valid_since)
            if expire_at is not Unspecified:
                q = q.filter_by(expire_at=expire_at)
            (membership_id,) = q.one()
        except NoResultFound:
            pass
        return membership_id

    def convert_to_record(self, reader, raw_record):
        with DictBuilder((MemberImportExportError, )) as b:
            member_set = None
            b['auth_identifier'] = required(reader, raw_record, u'auth_identifier', six.text_type)
            b['auth_secret'] = optional(reader, raw_record, u'auth_secret', six.text_type)
            b['name'] = optional(reader, raw_record, u'name', six.text_type)
            b['member_set'] = member_set = self._resolve_member_set(reader, u'member_set', required(reader, raw_record, u'member_set', six.text_type))
            b['member_kind'] = member_set and self._resolve_member_kind(reader, u'member_kind', member_set, optional(reader, raw_record, u'member_kind', six.text_type))
            b['membership_identifier'] = optional(reader, raw_record, u'membership_identifier', six.text_type)
            b['valid_since'] = parse_datetime(reader, raw_record, u'valid_since')
            expire_at = parse_datetime(reader, raw_record, u'expire_at')
            if expire_at is not None and expire_at is not Unspecified:
                expire_at = expire_at.replace(second=59, microsecond=0)
                expire_at += ONE_SECOND
            b['expire_at'] = expire_at
            b['email'] = raw_record.get('email') or Unspecified
            b['given_name'] = raw_record.get('given_name') or Unspecified
            b['family_name'] = raw_record.get('family_name') or Unspecified
            b['given_name_kana'] = raw_record.get('given_name_kana') or Unspecified
            b['family_name_kana'] = raw_record.get('family_name_kana') or Unspecified
            b['birthday'] = parse_date(reader, raw_record, u'birthday')
            b['gender'] = parse_gender(reader, raw_record, u'gender')
            b['country'] = raw_record.get('country') or Unspecified
            b['zip'] = raw_record.get('zip') or Unspecified
            b['prefecture'] = raw_record.get('prefecture') or Unspecified
            b['city'] = raw_record.get('city') or Unspecified
            b['address_1'] = raw_record.get('address_1') or Unspecified
            b['address_2'] = raw_record.get('address_2') or Unspecified
            b['tel_1'] = raw_record.get('tel_1') or Unspecified
            b['tel_2'] = raw_record.get('tel_2') or Unspecified
            b['deleted'] = bool(strip(raw_record.get(u'deleted', u'')))
        return b.errors, b.result

    def validate(self, reader, record):
        errors = []
        errors.extend(validate_length(reader, record, 'auth_identifier', min=1, max=128))
        errors.extend(validate_term(reader, record, 'valid_since', 'expire_at'))
        auth_identifier = record['auth_identifier']
        member_desc = self.members.get(auth_identifier)
        member_id = None
        if record['auth_secret'] is not Unspecified and \
           record['auth_secret'].startswith(HASH_SIGNATURE) and \
           len(record['auth_secret']) != len(HASH_SIGNATURE) + DIGESTED_SECRET_LEN:
            errors.append(
                MemberImportExportError.from_reader(
                    reader, [u'auth_secret'],
                    message=u'「%s」の値が不正です' % reader.column_name_map[u'auth_secret']
                    )
                )
        if member_desc is not None:
            if record['auth_secret'] is not Unspecified and \
               member_desc['auth_secret'] is not Unspecified and  \
               member_desc['auth_secret'] != record['auth_secret']:
                errors.append(
                    MemberImportExportError.from_reader(
                        reader, [u'auth_secret'],
                        message=u'「%s」の値が一貫していません' % reader.column_name_map[u'auth_secret']
                        )
                    )
            if record['member_set'] is not Unspecified and \
               member_desc['member_set'] is not Unspecified and  \
               member_desc['member_set'] != record['member_set']:
                errors.append(
                    MemberImportExportError.from_reader(
                        reader, [u'member_set'],
                        message=u'「%s」の値が一貫していません' % reader.column_name_map[u'member_set']
                        )
                    )
            if record['name'] is not Unspecified and \
               member_desc['name'] is not Unspecified and  \
               member_desc['name'] != record['name']:
                errors.append(
                    MemberImportExportError.from_reader(
                        reader, [u'name'],
                        message=u'「%s」の値が一貫していません' % reader.column_name_map[u'name']
                        )
                    )
            member_id = member_desc['member_id']
        else:
            try:
                member_id, = self.slave_session.query(Member.id) \
                    .filter_by(member_set_id=record['member_set'].id,
                               auth_identifier=auth_identifier) \
                    .one()
            except NoResultFound:
                pass
        record['member_id'] = member_id
        if member_id is not None and record['member_kind'] is not None:
            membership_id = self._resolve_membership(reader, member_id, record['member_kind'], record['membership_identifier'], record['valid_since'], record['expire_at'])
        else:
            membership_id = None
        if record['deleted'] and membership_id is None:
            errors.append(
                MemberImportExportError.from_reader(
                    reader, [u'deleted'],
                    message=u'既存のレコードではありませんが「%(deleted)s」が指定されています' % dict(
                        deleted=reader.column_name_map[u'deleted']
                        )
                    )
                )
        record['membership_id'] = membership_id
        return errors

    def __call__(self, reader):
        for raw_record in reader:
            errors_for_row, record = self.convert_to_record(reader, raw_record)
            if not errors_for_row:
                errors_for_row.extend(self.validate(reader, record))
            if not errors_for_row:
                auth_identifier = record['auth_identifier']
                member_desc = self.members.get(auth_identifier)
                if member_desc is not None:
                    if record['auth_secret'] is not Unspecified:
                        member_desc['auth_secret'] = record['auth_secret']
                else:
                    self.members[auth_identifier] = dict(
                        member_id=record['member_id'],
                        member_set=record['member_set'],
                        auth_secret=record['auth_secret'],
                        name=record['name']
                        )
            yield errors_for_row, record


class MemberDataWriterAdapter(object):
    def __init__(self, datetime_formatter, date_formatter):
        self.datetime_formatter = datetime_formatter
        self.date_formatter = date_formatter

    def format_ternary(self, v):
        if v:
            return u'*'
        elif v is not None:
            return u''
        else:
            return u''

    def format_gender(self, v):
        if v is None:
            return u''
        elif v == 0:
            return u'N'
        elif v == 1:
            return u'M'
        elif v == 2:
            return u'F'
        else:
            return u'???'

    def __call__(self, writer, exporter, ignore_close_error=False):
        num_records = 0
        try:
            for record in exporter:
                row = {
                    'auth_identifier':       record['auth_identifier'] or u'',
                    'auth_secret':           record['auth_secret'] or u'',
                    'name':                  record['name'] or u'',
                    'membership_identifier': record['membership_identifier'] or u'',
                    'member_set':            record['member_set'] or u'',
                    'member_kind':           record['member_kind'] or u'',
                    'email':                 record['email'] or u'',
                    'given_name':            record['given_name'] or u'',
                    'family_name':           record['family_name'] or u'',
                    'given_name_kana':       record['given_name_kana'] or u'',
                    'family_name_kana':      record['family_name_kana'] or u'',
                    'gender':                self.format_gender(record['gender']),
                    'country':               record['country'] or u'',
                    'zip':                   record['zip'] or u'',
                    'prefecture':            record['prefecture'] or u'',
                    'city':                  record['city'] or u'',
                    'address_1':             record['address_1'] or u'',
                    'address_2':             record['address_2'] or u'',
                    'tel_1':                 record['tel_1'] or u'',
                    'tel_2':                 record['tel_2'] or u'',
                    'deleted':               self.format_ternary(record.get('deleted', None)),
                    }
                if writer.datetime_conversion_needed:
                    row['valid_since'] = self.datetime_formatter(record['valid_since']) if record['valid_since'] is not None else u''
                    row['expire_at'] = self.datetime_formatter(record['expire_at'] - ONE_SECOND) if record['expire_at'] is not None else u''
                    row['birthday'] = self.date_formatter(record['birthday']) if record['birthday'] is not None else u''
                else:
                    row['valid_since'] = record['valid_since'] or u''
                    row['expire_at'] = (record['expire_at']  - ONE_SECOND) if record['expire_at'] is not None else u''
                    row['birthday'] = record['birthday'] if record['birthday'] is not None else u''
                writer(row)
                num_records += 1
        finally:
            try:
                writer.close()
            except:
                if not ignore_close_error:
                    raise
        return num_records


class MemberDataImporter(object):
    def __init__(self, master_session, organization_id):
        self.master_session = master_session
        self.organization_id = organization_id
        self.members_reflected = {}

    def map_to_member_column(self, record):
        auth_secret = record['auth_secret']
        if auth_secret is not Unspecified:
            if auth_secret.startswith(HASH_SIGNATURE):
                auth_secret = auth_secret[len(HASH_SIGNATURE):]
            else:
                auth_secret = digest_secret(auth_secret, generate_salt())
        return dict(
            id=record['member_id'],
            name=record['name'] or u'',
            member_set_id=record['member_set'].id,
            auth_identifier=record['auth_identifier'],
            auth_secret=auth_secret,
            email=record['email'],
            given_name=record['given_name'],
            family_name=record['family_name'],
            given_name_kana=record['given_name_kana'],
            family_name_kana=record['family_name_kana'],
            gender=record['gender'],
            birthday=record['birthday'],
            country=record['country'],
            zip=record['zip'],
            prefecture=record['prefecture'],
            city=record['city'],
            address_1=record['address_1'],
            address_2=record['address_2'],
            tel_1=record['tel_1'],
            tel_2=record['tel_2']
            )

    def map_to_membership_column(self, record):
        return dict(
            id=record['membership_id'],
            member_id=record['member_id'],
            member_kind_id=record['member_kind'].id,
            membership_identifier=record['membership_identifier'],
            valid_since=record['valid_since'],
            expire_at=record['expire_at']
            )

    def __call__(self, parser):
        num_records = 0
        errors = []
        for errors_for_row, record in parser:
            num_records += 1
            if errors_for_row:
                errors.extend(errors_for_row)
                continue
            auth_identifier = record['auth_identifier']
            if auth_identifier in self.members_reflected:
                record['member_id'] = self.members_reflected[auth_identifier]
            else:
                if record['member_id'] is None:
                    result = self.master_session.execute(
                        sql.insert(
                            Member.__table__,
                            values={
                                k: v if v is not Unspecified else None
                                for k, v in self.map_to_member_column(record).items()
                                }
                            )
                        )
                    record['member_id'] = result.inserted_primary_key
                else:
                    self.master_session.execute(
                        sql.update(
                            Member.__table__,
                            values={
                                k: v
                                for k, v in self.map_to_member_column(record).items()
                                if v is not Unspecified
                                },
                            whereclause=(Member.id == record['member_id'])
                            )
                        )
                self.members_reflected[auth_identifier] = record['member_id']
            if record['membership_id'] is None and record['member_kind'] is not None:
                result = self.master_session.execute(
                    sql.insert(
                        Membership.__table__,
                        values={
                            k: v if v is not Unspecified else None
                            for k, v in self.map_to_membership_column(record).items()
                            }
                        )
                    )
                record['membership_id'] = result.inserted_primary_key
            else:
                if record['deleted']:
                    self.master_session.execute(
                        sql.delete(
                            Membership.__table__,
                            whereclause=(Membership.id == record['membership_id'])
                            )
                        )
                else:
                    if record['member_kind'] is not None:
                        self.master_session.execute(
                            sql.update(
                                Membership.__table__,
                                values={
                                    k: v
                                    for k, v in self.map_to_membership_column(record).items()
                                    if v is not Unspecified
                                    },
                                whereclause=(Membership.id == record['membership_id'])
                                )
                            )
        if errors:
            raise MemberImportExportErrors(u'インポート中にエラーが発生しました', errors_for_row, num_records)
        return num_records

class MemberDeleteImporter(object):
    def __init__(self, master_session, organization_id):
        self.master_session = master_session
        self.organization_id = organization_id

    def __call__(self, parser):
        num_records = 0
        errors = []
        for errors_for_row, record in parser:
            num_records += 1
            if errors_for_row:
                errors.extend(errors_for_row)
                continue
            auth_identifier = record['auth_identifier']
            query = self.master_session.query(Member).filter(Member.auth_identifier == auth_identifier)
            n = query.delete(False)
            self.master_session.commit()

        if errors:
            raise MemberImportExportErrors(u'削除インポート中にエラーが発生しました', errors_for_row, num_records)
        return num_records

class MemberDataExporter(object):
    record_spec = [
        ('auth_identifier',       Member.auth_identifier),
        ('auth_secret',           Member.auth_secret),
        ('name',                  Member.name),
        ('membership_identifier', Membership.membership_identifier),
        ('member_set',            MemberSet.name),
        ('member_kind',           MemberKind.name),
        ('valid_since',           Membership.valid_since),
        ('expire_at',             Membership.expire_at),
        ('email',                 Member.email),
        ('given_name',            Member.given_name),
        ('family_name',           Member.family_name),
        ('given_name_kana',       Member.given_name_kana),
        ('family_name_kana',      Member.family_name_kana),
        ('birthday',              Member.birthday),
        ('gender',                Member.gender),
        ('country',               Member.country),
        ('zip',                   Member.zip),
        ('prefecture',            Member.prefecture),
        ('city',                  Member.city),
        ('address_1',             Member.address_1),
        ('address_2',             Member.address_2),
        ('tel_1',                 Member.tel_1),
        ('tel_2',                 Member.tel_2),
        ('deleted',               False),
        ]
    select_from = Member.__table__ \
        .join(MemberSet.__table__, Member.member_set_id == MemberSet.id) \
        .outerjoin(Membership.__table__, Member.id == Membership.member_id) \
        .outerjoin(MemberKind.__table__, Membership.member_kind_id == MemberKind.id)

    def __init__(self, request, slave_session, organization_id):
        self.request = request
        self.slave_session = slave_session
        self.organization_id = organization_id

    def __iter__(self):
        q = sql.select([c for _, c in self.record_spec]) \
            .select_from(self.select_from) \
            .where(MemberSet.organization_id == self.organization_id) \
            .order_by(Member.id)

        if self.request.params.get('member_set_id'):
                q = q.where(MemberSet.id==self.request.params.get('member_set_id'))
        if self.request.params.get('member_kind_id'):
                q = q.where(MemberKind.id==self.request.params.get('member_kind_id'))
        if self.request.params.get('search_name'):
                q = q.where(Member.name.like(u"%%%s%%" % self.request.params.get('search_name')))
        if self.request.params.get('search_auth_identifier'):
                q = q.where(Member.auth_identifier==self.request.params.get('search_auth_identifier'))
        if self.request.params.get('search_tel_1'):
                q = q.where(Member.tel_1==self.request.params.get('search_tel_1'))

        for raw_record in self.slave_session.execute(q):
            record = {k: v for (k, _), v in zip(self.record_spec, raw_record)}
            if record['auth_secret']:
                record['auth_secret'] = HASH_SIGNATURE + record['auth_secret']
            yield record
