# -*- coding:utf-8 -*-
from collections import OrderedDict

"""
- Order
- Performance
- SalesSegment
- PDMP
- PaymentMethod
- DeliveryMethod
- outer User
- outer UserProfile
- outer UserCredential
- outer ShippingAddress


CREATE TABLE `Order` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `user_id` bigint(20) DEFAULT NULL,
  `shipping_address_id` bigint(20) DEFAULT NULL,
  `organization_id` bigint(20) DEFAULT NULL,
  `total_amount` decimal(16,2) NOT NULL,
  `system_fee` decimal(16,2) NOT NULL,
  `transaction_fee` decimal(16,2) NOT NULL,
  `delivery_fee` decimal(16,2) NOT NULL,
  `multicheckout_approval_no` varchar(255) DEFAULT NULL,
  `payment_delivery_method_pair_id` bigint(20) DEFAULT NULL,
  `paid_at` datetime DEFAULT NULL,
  `delivered_at` datetime DEFAULT NULL,
  `canceled_at` datetime DEFAULT NULL,
  `order_no` varchar(255) DEFAULT NULL,
  `performance_id` bigint(20) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `deleted_at` timestamp NULL DEFAULT NULL,
  `note` text,
  `issued` tinyint(1) DEFAULT '0',
  `issued_at` datetime DEFAULT NULL,
  `printed_at` datetime DEFAULT NULL,
  `branch_no` int(11) NOT NULL DEFAULT '1',
  `channel` int(11) DEFAULT NULL,
  `operator_id` bigint(20) DEFAULT NULL,
  `refunded_at` datetime DEFAULT NULL,
  `refund_id` bigint(20) DEFAULT NULL,
  `card_brand` varchar(20) DEFAULT NULL,
  `card_ahead_com_code` varchar(20) DEFAULT NULL,
  `card_ahead_com_name` varchar(20) DEFAULT NULL,
  `browserid` varchar(40) DEFAULT NULL,
  `sales_segment_id` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_Order_order_no_branch_no` (`order_no`,`branch_no`),
  KEY `user_id` (`user_id`),
  KEY `shipping_address_id` (`shipping_address_id`),
  KEY `organization_id` (`organization_id`),
  KEY `payment_delivery_method_pair_id` (`payment_delivery_method_pair_id`),
  KEY `performance_id` (`performance_id`),
  KEY `ix_Order_deleted_at` (`deleted_at`),
  KEY `Order_ibfk_6` (`operator_id`),
  KEY `Order_ibfk_7` (`refund_id`),
  KEY `Order_ibfk_8` (`sales_segment_id`),


ステータス
 受付済み 配送済み キャンセル
 発券済み 未発券
 未入金 入金済み 払戻予約 払戻済み

決済 PaymentMethod.name
配送
予約番号
予約日時
合計
配送先氏名
イベント
開演日時
カードブランド
仕向け先

"""

sql = """\
explain 
SELECT 
    CASE
        WHEN `Order`.canceled_at IS NOT NULL
        THEN 'canceled'
        WHEN `Order`.delivered_at IS NOT NULL
        THEN 'delivered'
        ELSE 'ordered'
    END AS status,
    CASE
        WHEN `Order`.canceled_at IS NOT NULL
        THEN 'キャンセル'
        WHEN `Order`.delivered_at IS NOT NULL
        THEN '配送済み'
        ELSE '受付済み'
    END AS status_label, -- ステータス
    CASE
        WHEN `Order`.canceled_at IS NOT NULL
        THEN 'important'
        WHEN `Order`.delivered_at IS NOT NULL
        THEN 'success'
        ELSE 'warning'
    END AS status_class, -- success, inverse
    CASE
        WHEN `Order`.refund_id IS NOT NULL and `Order`.refunded_at IS NULL
        THEN 'refunding'
        WHEN `Order`.refunded_at IS NOT NULL
        THEN 'refunded'
        WHEN `Order`.paid_at IS NOT NULL
        THEN 'paid'
        ELSE 'unpaid'
    END AS payment_status,
    CASE
        WHEN `Order`.refund_id IS NOT NULL and `Order`.refunded_at IS NULL
        THEN '払戻予約' -- XXX (中止)の場合がある
        WHEN `Order`.refunded_at IS NOT NULL
        THEN '払戻済み' -- XXX (中止)の場合がある
        WHEN `Order`.paid_at IS NOT NULL
        THEN '入金済み'
        ELSE '未入金'
    END AS payment_status_label,
    CASE
        WHEN `Order`.refund_id IS NOT NULL and `Order`.refunded_at IS NULL
        THEN 'warning'
        WHEN `Order`.refunded_at IS NOT NULL
        THEN 'important'
        WHEN `Order`.paid_at IS NOT NULL
        THEN 'success'
        ELSE 'inverse'
    END AS payment_status_style,
    `Order`.order_no, -- 予約番号
    `Order`.created_at, -- 予約日時
    `Order`.total_amount, -- 合計
    ShippingAddress.last_name + ' ' + ShippingAddress.first_name, -- 配送先氏名
    Event.title, -- イベント
    Performance.start_on, -- 開演日時
    `Order`.card_brand, -- カードブランド
    `Order`.card_ahead_com_name, -- 仕向け先
    NULL
FROM `Order`
    JOIN Performance
    ON `Order`.performance_id = Performance.id
    AND Performance.deleted_at IS NULL
    JOIN Event
    ON Performance.event_id = Event.id
    AND Event.deleted_at IS NULL
    JOIN SalesSegment
    ON `Order`.sales_segment_id = SalesSegment.id
    AND SalesSegment.deleted_at IS NULL
JOIN PaymentDeliveryMethodPair AS PDMP
    ON `Order`.payment_delivery_method_pair_id = PDMP.id
    AND PDMP.deleted_at IS NULL
    JOIN PaymentMethod
    ON PDMP.payment_method_id = PaymentMethod.id
    AND PaymentMethod.deleted_at IS NULL
    JOIN DeliveryMethod
    ON PDMP.delivery_method_id = DeliveryMethod.id
    AND DeliveryMethod.deleted_at IS NULL
    LEFT JOIN ShippingAddress
    ON `Order`.shipping_address_id = ShippingAddress.id
    AND ShippingAddress.deleted_at IS NULL
    LEFT JOIN User
    ON `Order`.user_id = User.id
    AND User.deleted_at IS NULL
    LEFT JOIN UserProfile
    ON User.id = UserProfile.user_id
    AND UserProfile.deleted_at IS NULL
    LEFT JOIN UserCredential
    ON User.id = UserCredential.user_id
    AND UserCredential.deleted_at IS NULL
    LEFT JOIN SejOrder
    ON `Order`.order_no = SejOrder.order_id
    AND SejOrder.deleted_at IS NULL
WHERE `Order`.deleted_at IS NULL
"""

# Userに対してUserProfileが複数あると行数が増える可能性

class OrderDownload(object):
    def __init__(self, db_session):
        self.db_session = db_session

    def query(self, condition, limit, offset):
        sql = self.sql
        params = ()
        if 'billing_or_exchange_number' in condition:
            pass

        if 'ordered_from' in condition:
            sql = sql + " AND `Order`.created_at >= %s"
            params = params + (condition['ordered_from'],)

        if 'ordered_to' in condition:
            sql = sql + " AND `Order`.created_at <= %s"
            params = params + (condition['ordered_to'],)

        if 'status' in condition:
            status_cond = []
            if 'ordered' in condition['status']:
                status_cond.append("(`Order`.canceled_at IS NULL AND `Order`.delivered_at IS NULL)")
            if 'delivered' in condition['status']:
                status_cond.append("(`Order`.canceled_at IS NULL AND `Order`.delivered_at IS NOT NULL)")
            if 'canceled' in condition['status']:
                status_cond.append("(`Order`.canceled_at IS NOT NULL)")
            
            if status_cond:
                sql = sql + " AND ( " + " OR ".join(status_cond) + " ) "

        if 'issue_status' in condition:
            issue_cond = []
            if 'issued' in condition['issue_status']:
                issue_cond.append(' `Order`.issued = 1 ')
            if 'unissued' in condition['issue_status']:
                issue_cond.append(' `Order`.issued = 0 ')

            if issue_cond:
                sql = sql + " AND ( " + " OR ".join(issue_cond) + " ) "

        if 'payment_status' in condition:
            # unpaid, paid, refunding, refunded
            payment_cond = []
            if 'unpaid' in condition['payment_status']:
                payment_cond.append("(`Order`.refunded_at IS NULL "
                                    " AND `Order`.refund_id IS NULL "
                                    " AND `Order`.paid_at IS NULL ) ")

            if 'paid' in condition['payment_status']:
                payment_cond.append("(`Order`.refunded_at IS NULL "
                                    " AND `Order`.refund_id IS NULL "
                                    " AND `Order`.paid_at IS NOT NULL ) ")

            if 'refunding' in condition['payment_status']:
                payment_cond.append("(`Order`.refunded_at IS NULL "
                                    " AND `Order`.refund_id IS NOT NULL ) ")
            if 'refunded' in condition['payment_status']:
                payment_cond.append("(`Order`.refunded_at IS NOT NULL ) ")


            if payment_cond:
                sql = sql + " AND ( " + " OR ".join(payment_cond) + " ) "

        if 'member_id' in condition:
            sql = sql + " AND UserCredential.auth_identifier = %s"
            params += (condition['memger_id'],)

        if 'number_of_tickets' in condition and (condition.get('event_id') or condition.get('performance_id')):
            
            cond = """ AND `Order`.id in (
            SELECT OrderedProduct.order_id AS order_id,
            FROM OrderedProduct
            JOIN OrderedProductItem
            ON OrderedProduct.id = OrderedProductItem.ordered_product_id
            AND OrderedProductItem.deleted_at IS NULL
            JOIN ProductItem
            ON OrderedProductItem.product_item_id = ProductItem.id
            AND ProductItem.deleted_at IS NULL
            JOIN Performance
            ON ProductItem.performance_id = Performance.id
            AND Performance.deleted_at IS NULL
            WHERE OrderedProduct.deleted_at IS NULL
            """

            if condition.get('event_id'):
                cond = cond + " AND Performance.event_id = %s"
                params += (condition['event_id'],)
            if condition.get('performance_id'):
                cond = cond + " AND Performance.id = %s"
                params += (condition['performance_id'],)


            cond = cond + """
            GROUP BY OrderedProduct.order_id
            HAVING sum(ProductItem.quantity) >= %s)
            """
            params += (condition['number_of_tickets'],)

            sql = sql + cond
        # order by
        if 'sort' in condition:
            if 'direction' in condition:
                # asc, desc
                pass
            else:
                pass

        return sql

    def __iter__(self, columns, condition):
        cur = self.db_session.bind.execute(self.query(condition))
        try:
            for row in cur.fetchall():
                yield OrderedDict([
                    (c, row[c])
                    for c in columns]
                )
        finally:
            cur.close()
