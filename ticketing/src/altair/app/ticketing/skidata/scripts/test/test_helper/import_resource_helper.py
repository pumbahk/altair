#! /usr/bin/env python
# coding=utf-8
import csv
from datetime import datetime
import sqlalchemy
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

TABLE_NAME_PREFIX = 'table_name_'


def importer_tables(session, tables_meta, file_name, except_keys):
    tables_id_dict = dict()
    with open(file_name, 'r') as f:
        reader = csv.reader(f)
        headers_list = _get_headers_list(next(reader, None))
        for row in reader:
            for table_info in headers_list:
                table = _create_table_data(table_info, tables_meta, row, except_keys)
                if hasattr(table, 'id') and _is_have_duplicate_id(tables_id_dict, table_info.table_name, table.id):
                    continue
                session.add(table)
    session.flush()


def _is_have_duplicate_id(tables_id_dict, table_name, row_id):
    ids_list = tables_id_dict.get(table_name, None)
    if ids_list is None:
        ids_list = list()
        tables_id_dict[table_name] = ids_list
    if row_id in ids_list:
        return True
    ids_list.append(row_id)
    return False


def _create_table_data(table_info, tables_meta, row, except_keys):
    table_name = table_info.table_name
    column_names = table_info.column_names
    columns = tables_meta.tables[table_name].columns
    table = _get_table_obj(table_name)

    for index_column in range(len(column_names)):
        item_key = column_names[index_column]
        if except_keys is not None and item_key in except_keys:
            continue
        if hasattr(table, item_key):
            item_type = columns[item_key].type
            item_value = _get_item_value(item_type, row[table_info.start_index + index_column])
            if item_value is None:
                continue
            try:
                setattr(table, item_key, item_value)
            except Exception as e:
                print(e, table_name, item_type, item_key, item_value)
    return table


class TableInfo(object):
    table_name = None
    start_index = -1
    column_names = None


def _get_headers_list(headers):
    headers_list = list()
    table_info = None
    for index_item in range(len(headers)):
        value = headers[index_item]
        if value.startswith(TABLE_NAME_PREFIX):
            table_name = value.replace(TABLE_NAME_PREFIX, '')
            table_info = _get_table_info(table_name, index_item)
            headers_list.append(table_info)
            continue
        table_info.column_names.append(value)
    return headers_list


def _get_table_info(value, i):
    table_info = TableInfo()
    table_info.table_name = value
    table_info.start_index = i + 1
    table_info.column_names = list()
    return table_info


def _get_item_value(column_type, item_value):
    if item_value is None or item_value == '':
        return None
    if isinstance(column_type, sqlalchemy.types.Time):
        time_data = convert2datetime(item_value, '%H:%M:%S')
        item_value = time_data.time() if time_data else None
    elif isinstance(column_type, sqlalchemy.types.TIMESTAMP) or isinstance(column_type, sqlalchemy.types.DATETIME):
        item_value = convert2datetime(item_value, '%Y-%m-%d %H:%M:%S')
    elif isinstance(column_type, sqlalchemy.types.INTEGER):
        item_value = int(item_value)
    elif isinstance(column_type, sqlalchemy.types.String):
        item_value = unicode(item_value)
    return item_value


def convert2datetime(time_str, format_str):
    try:
        return datetime.strptime(time_str, format_str)
    except ValueError:
        return None


def _get_table_obj(table_name):
    import importlib
    module = importlib.import_module("altair.app.ticketing.core.models")
    if not hasattr(module, table_name):
        module = importlib.import_module("altair.app.ticketing.orders.models")
    if not hasattr(module, table_name):
        module = importlib.import_module("altair.app.ticketing.skidata.models")
    class_ = getattr(module, table_name)
    return class_()
