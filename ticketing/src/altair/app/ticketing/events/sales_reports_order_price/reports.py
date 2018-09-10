# -*- coding: utf-8 -*-
import codecs
import logging
import os
import shutil
import sqlalchemy as sa
import uuid
from altair.app.ticketing.core.models import Event, Performance, StockType, ProductItem, Stock, StockStatus, \
    SalesSegment, SalesSegmentGroup, Product
from altair.app.ticketing.events.auto_cms.api import s3upload, S3ConnectionFactory
from altair.app.ticketing.orders.models import Order, OrderedProduct, OrderedProductItem
from altair.app.ticketing.resources import TicketingAdminResource
from altair.sqlahelper import get_db_session
from boto.exception import S3ResponseError
from collections import namedtuple
from datetime import datetime

S3_DIRECTORY = "sales_report_order_price/{}/"
file_name_format = u"売上げレポート{0}_レポート非対称含む.csv"
file_path_format = u"{0}売上げレポート{1}_レポート非対称含む.csv"
file_name_format_reporting = u"売上げレポート{0}.csv"
file_path_format_reporting = u"{0}売上げレポート{1}.csv"
logger = logging.getLogger(__name__)


class SalesReporterOrderPrice(object):
    """
    予約ごとのレポートを出力する

    Attributes
    ----------
    __sales_report_events : list
        出力するイベントのリスト
    __organization_id : int
        出力対象のORGのID
    __slave_session : SESSION
        DBSESSION
    report_data : sql
        レポート出力のクエリ
    __outputer : Outputer
        出力用クラス
    """

    def __init__(self, request, outputer, organization_id):
        """
        Parameters
        ----------
        request : request
            リクエスト
        outputer : Outputer
            出力用クラス
        organization_id : int
            出力するORGのID
        """
        # 売上げレポートの対象は、procuction/conf/altair.ticketing.batch.iniに記載。
        # 開発環境とステージングは、common.iniファイルに記述。
        self.__sales_report_events = request.registry.settings["sales_reports_events"].split(",")
        self.__organization_id = organization_id
        self.__slave_session = get_db_session(request, name="slave")
        self.report_data = self.create_report_data()
        self.__outputer = outputer

    def create_report_data(self, reporting=False):
        # TODO SalesSegmentGroup.reportingを追加するためだけに分岐してしまっている。要修正
        if reporting:
            query = self.__slave_session.query(
                    Event.id.label('event_id'),
                    Event.title.label('event_title'),
                    Performance.code.label('performance_code'),
                    Performance.start_on.label('performance_start_on'),
                    Stock.id.label('stock_id'),
                    StockType.name.label('stock_type_name'),
                    Stock.quantity.label('stock_quantity'),
                    Stock.quantity - sa.func.sum(
                        OrderedProduct.quantity
                    ) * ProductItem.quantity.label('stock_status_quantity'),
                    SalesSegmentGroup.name.label('sales_segment_group_name'),
                    Product.name.label('product_name'),
                    OrderedProductItem.price.label('ordered_product_price'),
                    sa.func.sum(
                        OrderedProduct.quantity
                    ) * ProductItem.quantity.label('total_count'),
                    sa.func.sum(
                        sa.func.IF(
                            Order.paid_at != None , OrderedProduct.quantity, 0
                        )
                    ).label('purchace_count'),
                    sa.func.sum(
                        sa.func.IF(Order.paid_at == None, OrderedProduct.quantity * ProductItem.quantity, 0)
                    ).label('order_count'),
                    sa.func.sum(
                        OrderedProductItem.quantity
                    ) * OrderedProductItem.price.label('total_amount')
            ). \
                join(Performance, Performance.event_id == Event.id). \
                join(SalesSegment, SalesSegment.performance_id == Performance.id). \
                join(SalesSegmentGroup, SalesSegmentGroup.id == SalesSegment.sales_segment_group_id). \
                join(Order, Order.performance_id == Performance.id). \
                join(OrderedProduct, OrderedProduct.order_id == Order.id). \
                join(OrderedProductItem, OrderedProductItem.ordered_product_id == OrderedProduct.id). \
                join(Product, Product.id == OrderedProduct.product_id). \
                join(ProductItem, OrderedProductItem.product_item_id == ProductItem.id). \
                join(Stock, Stock.id == ProductItem.stock_id). \
                join(StockStatus, StockStatus.stock_id == Stock.id). \
                join(StockType, StockType.id == Product.seat_stock_type_id). \
                filter(SalesSegmentGroup.reporting == True). \
                filter(Order.canceled_at == None). \
                filter(Order.refunded_at == None). \
                filter(Event.organization_id == self.__organization_id). \
                filter(Event.id.in_(self.__sales_report_events)). \
                group_by(ProductItem.id, OrderedProductItem.price). \
                order_by(Event.id, Stock.id)
            return query.all()

        query = self.__slave_session.query(
                Event.id.label('event_id'),
                Event.title.label('event_title'),
                Performance.code.label('performance_code'),
                Performance.start_on.label('performance_start_on'),
                Stock.id.label('stock_id'),
                StockType.name.label('stock_type_name'),
                Stock.quantity.label('stock_quantity'),
                Stock.quantity - sa.func.sum(
                    OrderedProduct.quantity
                ) * ProductItem.quantity.label('stock_status_quantity'),
                SalesSegmentGroup.name.label('sales_segment_group_name'),
                Product.name.label('product_name'),
                OrderedProductItem.price.label('ordered_product_price'),
                sa.func.sum(
                    OrderedProduct.quantity
                ) * ProductItem.quantity.label('total_count'),
                sa.func.sum(
                    sa.func.IF(
                        Order.paid_at != None , OrderedProduct.quantity, 0
                    )
                ).label('purchace_count'),
                sa.func.sum(
                    sa.func.IF(Order.paid_at == None, OrderedProduct.quantity * ProductItem.quantity, 0)
                ).label('order_count'),
                sa.func.sum(
                    OrderedProductItem.quantity
                ) * OrderedProductItem.price.label('total_amount')
        ). \
            join(Performance, Performance.event_id == Event.id). \
            join(SalesSegment, SalesSegment.performance_id == Performance.id). \
            join(SalesSegmentGroup, SalesSegmentGroup.id == SalesSegment.sales_segment_group_id). \
            join(Order, Order.performance_id == Performance.id). \
            join(OrderedProduct, OrderedProduct.order_id == Order.id). \
            join(OrderedProductItem, OrderedProductItem.ordered_product_id == OrderedProduct.id). \
            join(Product, Product.id == OrderedProduct.product_id). \
            join(ProductItem, OrderedProductItem.product_item_id == ProductItem.id). \
            join(Stock, Stock.id == ProductItem.stock_id). \
            join(StockStatus, StockStatus.stock_id == Stock.id). \
            join(StockType, StockType.id == Product.seat_stock_type_id). \
            filter(Order.canceled_at == None). \
            filter(Order.refunded_at == None). \
            filter(Event.organization_id == self.__organization_id). \
            filter(Event.id.in_(self.__sales_report_events)). \
            group_by(ProductItem.id, OrderedProductItem.price). \
            order_by(Event.id, Stock.id)
        return query.all()

    def output_report(self, reporting=False):
        return self.__outputer.output_report(self, reporting)


class SalesReportOutputer:
    """
    レポート結果を出力する抽象クラス
    """
    def __init__(self):
        pass

    def output_report(self, report, reporting=False):
        raise Exception('Called abstract method.')


class S3SalesReportOutputer(SalesReportOutputer):
    """
    S3にレポート結果を出力するクラス

    Attributes
    ----------
    request : request
        リクエスト
    path : str
        出力するパス
    """
    def __init__(self, request, path):
        """
        Parameters
        ----------
        request : request
            リクエスト
        path : str
            出力するパス
        """
        self.request = request
        self.path = path

    def output_report(self, report, reporting=False):
        """
        S3へ結果を出力する

        Parameters
        ----------
        report : SalesReporterOrderPrice
            レポートオブジェクト
        reporting : bool
            売上げレポート対象かのフラグ

        Returns
        ----------
        file
            ファイル
        """
        event_names = create_csv(report, self.path, reporting)
        for event_name in event_names:
            connection = S3ConnectionFactory(self.request)()
            now = datetime.now()
            today_str = now.strftime('%Y-%m-%d')
            bucket_name = self.request.registry.settings["s3.bucket_name"]
            file_path = file_path_format_reporting.format(
                self.path, event_name) if reporting else file_path_format.format(self.path, event_name)
            file_name = file_name_format_reporting.format(
                event_name) if reporting else file_name_format.format(event_name)
            try:
                s3upload(connection, bucket_name, file_path,
                         S3_DIRECTORY.format(today_str), file_name)
                logger.info(u"sales_report_order_price s3 upload={}".format(file_name))
            except S3ResponseError as e:
                logger.error("SalesReportsOrderPrice did not save. file_name={}".format(file_name))
            os.remove(file_path)


class CsvSalesReportOutputer(SalesReportOutputer):
    """
    CSVにレポート結果を出力するクラス

    Attributes
    ----------
    request : request
        リクエスト
    path : str
        出力するパス
    """
    def __init__(self, request, path):
        """
        Parameters
        ----------
        request : request
            リクエスト
        path : str
            出力するパス
        """
        self.request = request
        self.path = path

    def output_report(self, report, reporting=False):
        """
        CSVへ結果を出力する

        Parameters
        ----------
        report : SalesReporterOrderPrice
            レポートオブジェクト
        reporting : bool
            売上げレポート対象かのフラグ

        Returns
        ----------
        file
            ファイル
        """
        create_csv(report, self.path, reporting)


def create_csv(report, path, reporting=False):
    """
    SalesReporterOrderPriceから、CSVを作成する

    Parameters
    ----------
    report : SalesReporterOrderPrice
        レポートオブジェクト
    path : str
        ファイルの出力パス
    reporting : bool
        売上げレポート対象かのフラグ

    Returns
    ----------
    event_titles : list
        出力したファイルのイベントタイトルのリスト
    """

    header = u"公演コード,公演日時,Stock,席種,配席数,残数,販売区分,商品,価格,受付数,購入確定数,予約数,受付金額\n"
    Column = namedtuple('Column', (
        'event_id', 'event_title', 'performance_code', 'performance_start_on', 'stock_id', 'stock_type_name',
        'stock_quantity', 'stock_status_quantity', 'sales_segment_group_name', 'product_name', 'ordered_product_price',
        'total_count', 'purchace_count', 'order_count', 'total_amount'))
    col = Column(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14)

    stock_id = None
    event_title = None
    event_titles = []
    for data in report.report_data:

        output_list = list(data)

        if not event_title or event_title != output_list[col.event_title]:
            if event_title:
                f.close()
            event_title = output_list[col.event_title]
            file_path = file_path_format_reporting.format(path, output_list[col.event_title])\
                if reporting else file_path_format.format(path, output_list[col.event_title])
            event_titles.append(output_list[col.event_title])
            f = codecs.open(file_path, 'w', 'utf-8-sig')
            logger.info(u"sales_report_order_price create file={}".format(file_path))
            f.write(header)

        output_list[col.performance_start_on] = unicode(
            output_list[col.performance_start_on].strftime(u"%Y/%m/%d %H:%M"))
        output_list[col.stock_id] = unicode(output_list[col.stock_id])
        output_list[col.stock_quantity] = unicode(output_list[col.stock_quantity])
        output_list[col.stock_status_quantity] = unicode(output_list[col.stock_status_quantity])
        output_list[col.ordered_product_price] = unicode(int(output_list[col.ordered_product_price]))
        output_list[col.total_count] = unicode(int(output_list[col.total_count]))
        output_list[col.purchace_count] = unicode(int(output_list[col.purchace_count]))
        output_list[col.order_count] = unicode(int(output_list[col.order_count]))
        output_list[col.total_amount] = unicode(int(output_list[col.total_amount]))

        if not stock_id or stock_id != output_list[col.stock_id]:
            stock_id = output_list[col.stock_id]
            seat_num = output_list[col.performance_code:col.stock_status_quantity+1]
            seat_output = ",".join(seat_num)
            seat_output = u"{0}\n".format(seat_output)
            f.write(seat_output)

        output_list[col.stock_quantity] = output_list[col.stock_status_quantity] = u""

        del output_list[col.event_title]
        del output_list[col.event_id]
        output = ",".join(output_list)
        output = u"{0}\n".format(output)
        f.write(output)

    if report.report_data:
        f.close()
    return event_titles
