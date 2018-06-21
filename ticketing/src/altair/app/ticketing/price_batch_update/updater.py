# -*- coding: utf-8 -*-

from altair.app.ticketing.core.models import (
    Product
)
import csv
from collections import OrderedDict
from decimal import Decimal
import logging
from sqlalchemy import orm, and_
import sqlahelper
import traceback
from .models import (
    PriceBatchUpdateTaskStatusEnum,
    PriceBatchUpdateErrorEnum,
    PriceBatchUpdateTask
)

logger = logging.getLogger(__name__)


class _NoProductError(Exception):
    pass


class _SameNameProductError(Exception):
    pass


class _MultiItemsProductError(Exception):
    pass


class _ProcessingBatchError(Exception):
    batch_error_code = None

    def __init__(self, code):
        self.batch_error_code = code


class PriceCsvRow(object):
    performance_id = None
    product_name = None
    price_optimized = None


def read_price_csv(csv_file, encoding='cp932'):
    price_csv_rows = []

    for index, line in enumerate(csv.DictReader(csv_file)):
        price_csv_row = PriceCsvRow()
        try:
            price_csv_row.performance_id = long(line['performance_id']) \
                if 'performance_id' in line and line['performance_id'] else None
        except ValueError:
            logger.warn('csv-line {0}: performance_id is not numeric.'.format(index + 1))

        try:
            price_csv_row.product_name = unicode(line['product_name'].decode(encoding)) \
                if 'product_name' in line and line['product_name'] else None
        except UnicodeDecodeError:
            logger.warn('csv-line {0}: failed to decode product_name with {1}.'.format(index + 1, encoding))

        try:
            price_csv_row.price_optimized = long(line['price_optimized']) \
                if 'price_optimized' in line and line['price_optimized'] else None
        except ValueError:
            logger.warn('csv-line {0}: price_optimized is not numeric.'.format(index + 1))

        price_csv_rows.append(price_csv_row)

    return price_csv_rows


def validate_price_csv(csv_rows, performance, target_sales_segment_ids):
    target_sales_segments = [ss for ss in performance.sales_segments if ss.id in target_sales_segment_ids]
    error_dict = OrderedDict()

    for index, row in enumerate(csv_rows):
        errors = _validate_price_csv_row(row, performance, target_sales_segments)
        if len(errors) > 0:
            error_dict.update({index + 1: errors})

    product_count_to_update = len(csv_rows) * len(target_sales_segments)

    return product_count_to_update, error_dict


def _validate_price_csv_row(row, performance, sales_segments):
    errors = []

    if row.performance_id != performance.id:
        errors.append(u'公演IDが一致しないか、存在しません。')
    if not row.price_optimized:
        errors.append(u'価格が指定されていないか、不正な形式です。')
    if not row.product_name:
        errors.append(u'商品名が指定されていないか、不正な形式です。')
    else:
        for ss in sales_segments:
            try:
                target_product = [p for p in ss.products if p.name == row.product_name and p.public]
                _validate_product(target_product)
            except _NoProductError:
                errors.append(u'商品({0})は販売区分({1})に存在しないか、非公開です。'.format(row.product_name, ss.name))
            except _SameNameProductError:
                errors.append(u'商品({0})は販売区分({1})に複数存在します。'.format(row.product_name, ss.name))
            except _MultiItemsProductError:
                errors.append(u'商品({0})に商品明細が複数存在します。'.format(row.product_name))

    return errors


def run_price_batch_update_task(task_id):
    # altair.app.ticketing.models.DBSession出ない場合はLogicallyDeletedが効かないことに注意
    task_session = orm.session.Session(bind=sqlahelper.get_engine())

    try:
        task = task_session.query(PriceBatchUpdateTask)\
            .filter(PriceBatchUpdateTask.id == task_id,
                    PriceBatchUpdateTask.status == PriceBatchUpdateTaskStatusEnum.Updating.v,
                    PriceBatchUpdateTask.deleted_at.is_(None)
        ).with_lockmode('update').first()
        count_updated = 0

        for entry in task.entries:
            count_updated += _process_price_batch_update_entry(entry)

        task.count_updated = count_updated
        task.status = PriceBatchUpdateTaskStatusEnum.Updated.v \
            if count_updated > 0 else PriceBatchUpdateTaskStatusEnum.Aborted.v

        if len(task.entries) == 0:
            task.error = PriceBatchUpdateErrorEnum.PDU_E_001.k
        elif count_updated == 0:
            task.error = PriceBatchUpdateErrorEnum.PDU_E_002.k
        elif len(task.entries) != count_updated:
            task.error = PriceBatchUpdateErrorEnum.PDU_W_001.k

        task_session.commit()
    except:
        task_session.rollback()
        logger.error('PriceBatchUpdateTask[id={0}] session has been rolled back: {1}'
                     .format(task_id, traceback.format_exc()))
    finally:
        task_session.close()


def _process_price_batch_update_entry(entry):
    # altair.app.ticketing.models.DBSession出ない場合はLogicallyDeletedが効かないことに注意
    product_session = orm.session.Session(bind=sqlahelper.get_engine())

    try:
        try:
            if not entry.sales_segment:
                raise _ProcessingBatchError(PriceBatchUpdateErrorEnum.PDU_PE_E_001.k)

            target_product = product_session.query(Product).filter(
                Product.sales_segment == entry.sales_segment,
                Product.name == entry.product_name,
                Product.public == 1,
                Product.deleted_at.is_(None)
            ).with_lockmode('update').all()

            _validate_entry_product(target_product)

            target_product[0].price = entry.price
            items = [item for item in target_product[0].items if item.deleted_at is None]
            if items[0]:
                items[0].price = entry.price / Decimal(items[0].quantity)
        except _ProcessingBatchError as batch_error:
            entry.error = batch_error.batch_error_code

        product_session.commit()
        return True if not entry.error else False
    except:
        product_session.rollback()
        entry.error = PriceBatchUpdateErrorEnum.PDU_PE_E_005.k
        logger.error('Product for PriceBatchUpdateEntry[id={0}] has been rolled back: {1}'
                     .format(entry.id, traceback.format_exc()))
        return False
    finally:
        product_session.close()


def _validate_entry_product(target_product):
    try:
        _validate_product(target_product)
    except _NoProductError:
        raise _ProcessingBatchError(PriceBatchUpdateErrorEnum.PDU_PE_E_002.k)
    except _SameNameProductError:
        raise _ProcessingBatchError(PriceBatchUpdateErrorEnum.PDU_PE_E_003.k)
    except _MultiItemsProductError:
        raise _ProcessingBatchError(PriceBatchUpdateErrorEnum.PDU_PE_E_004.k)


def _validate_product(target_product):
    if not target_product or len(target_product) == 0:
        raise _NoProductError()

    if len(target_product) > 1:
        raise _SameNameProductError()

    if len([item for item in target_product[0].items if item.deleted_at is None]) > 1:
        raise _MultiItemsProductError()
