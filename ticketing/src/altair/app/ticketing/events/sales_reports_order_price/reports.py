# -*- coding: utf-8 -*-
import codecs
import logging
import os
from collections import namedtuple
from datetime import datetime

import sqlalchemy as sa
from altair.app.ticketing.core.models import Event, Performance, StockType, ProductItem, Stock, StockStatus, \
    SalesSegment, SalesSegmentGroup, Product
from altair.app.ticketing.events.auto_cms.api import s3upload, S3ConnectionFactory
from altair.app.ticketing.orders.models import Order, OrderedProduct, OrderedProductItem
from altair.sqlahelper import get_db_session
from boto.exception import S3ResponseError

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
        self.__outputer = outputer
        self.report_data = None

    def create_report_data(self, reporting=False):
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
                * ProductItem.quantity).label('stock_status_quantity'),
            SalesSegmentGroup.name.label('sales_segment_group_name'),
            Product.name.label('product_name'),
            OrderedProductItem.price.label('ordered_product_price'),
            sa.func.sum(
                OrderedProduct.quantity
            ) * ProductItem.quantity.label('total_count'),
            sa.func.sum(
                sa.func.IF(
                    Order.paid_at != None, OrderedProduct.quantity * ProductItem.quantity, 0
                )
            ).label('purchace_count'),
            sa.func.sum(
                sa.func.IF(Order.paid_at == None, OrderedProduct.quantity * ProductItem.quantity, 0)
            ).label('order_count'),
            sa.func.sum(
                OrderedProductItem.quantity
                * OrderedProductItem.price).label('total_amount')
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
            join(StockType, StockType.id == Product.seat_stock_type_id)
        if reporting:
            query = query.filter(SalesSegmentGroup.reporting == True)
        query = query.filter(Order.canceled_at == None). \
            filter(Order.refunded_at == None). \
            filter(Event.organization_id == self.__organization_id). \
            filter(Event.id.in_(self.__sales_report_events)). \
            filter(SalesSegment.id == Order.sales_segment_id). \
            group_by(ProductItem.id, OrderedProductItem.price). \
            order_by(Event.id, Stock.id)
        self.report_data = query.all()

    def output_report(self, reporting=False):
        self.create_report_data(reporting)
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
            bucket_name = self.request.registry.settings["sales_report_order_price.s3.bucket_name"]
            file_path = file_path_format_reporting.format(
                self.path, event_name) if reporting else file_path_format.format(self.path, event_name)
            file_name = file_name_format_reporting.format(
                event_name) if reporting else file_name_format.format(event_name)
            try:
                s3upload(connection, bucket_name, file_path,
                         S3_DIRECTORY.format(today_str), file_name, public=False)
                logger.info(u"sales_report_order_price s3 upload={}".format(file_name))
            except S3ResponseError as e:
                logger.error(u"SalesReportsOrderPrice did not save. file_name={}".format(file_name))
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

    # 出力されたSQL結果から、行毎のリストを作成する。その後、リストを使用し、ファイルに書き込む
    # 残数の計算のみ難しく、このような対応にしている
    stock_id = None
    stock_status_quantity_dict = {}
    headers = []
    bodies = []
    for data in report.report_data:
        output_list = list(data)
        output_list[col.performance_start_on] = unicode(
            output_list[col.performance_start_on].strftime(u"%Y/%m/%d %H:%M"))
        output_list[col.stock_id] = unicode(output_list[col.stock_id])
        output_list[col.stock_quantity] = unicode(output_list[col.stock_quantity])
        output_list[col.ordered_product_price] = unicode(int(output_list[col.ordered_product_price]))
        output_list[col.total_count] = unicode(int(output_list[col.total_count]))
        output_list[col.purchace_count] = unicode(int(output_list[col.purchace_count]))
        output_list[col.order_count] = unicode(int(output_list[col.order_count]))
        output_list[col.total_amount] = unicode(int(output_list[col.total_amount]))

        # カンマが含まれていることを考慮
        output_list[col.event_title] = u"\"{0}\"".format(output_list[col.event_title])
        output_list[col.stock_type_name] = u"\"{0}\"".format(output_list[col.stock_type_name])
        output_list[col.product_name] = u"\"{0}\"".format(output_list[col.product_name])
        output_list[col.sales_segment_group_name] = u"\"{0}\"".format(output_list[col.sales_segment_group_name])

        if not stock_id or stock_id != output_list[col.stock_id]:
            stock_id = output_list[col.stock_id]
            headers.append(output_list)

        # 残数
        stock_status_quantity = 0
        if stock_id in stock_status_quantity_dict:
            stock_status_quantity = stock_status_quantity_dict[stock_id]
        stock_status_quantity_dict[stock_id] = stock_status_quantity + int(output_list[col.stock_quantity]) - int(
            output_list[col.stock_status_quantity])

        bodies.append(output_list)

    stock_id = None
    event_title = None
    event_titles = []
    for i, body_data in enumerate(bodies):

        if not event_title or event_title != body_data[col.event_title]:
            if event_title:
                f.close()
            event_title = body_data[col.event_title]
            file_path = file_path_format_reporting.format(path, body_data[col.event_title])\
                if reporting else file_path_format.format(path, body_data[col.event_title])
            event_titles.append(body_data[col.event_title])

            f = codecs.open(file_path, 'w', 'utf-8-sig')
            logger.info(u"sales_report_order_price create file={}".format(file_path))
            f.write(header)

        if not stock_id or stock_id != body_data[col.stock_id]:
            stock_id = body_data[col.stock_id]
            header_data = headers.pop(0)
            header_data[col.stock_status_quantity] = unicode(
                int(body_data[col.stock_quantity]) - stock_status_quantity_dict[stock_id])
            header_data = header_data[col.performance_code:col.stock_status_quantity+1]
            write_data(f, header_data)

        body_data[col.stock_quantity] = body_data[col.stock_status_quantity] = u""
        del body_data[col.event_title]
        del body_data[col.event_id]
        write_data(f, body_data)
    return event_titles


def write_data(fp, data):
    output = ",".join(data)
    output = u"{0}\n".format(output)
    fp.write(output)
