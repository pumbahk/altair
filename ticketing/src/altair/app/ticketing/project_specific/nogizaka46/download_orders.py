# encoding: utf-8

import csv
import argparse
from pymysql import connect, cursors


download_sql = """
select
	o.order_no as "予約番号",
	case 
		when o.canceled_at then "canceled"
		when o.delivered_at then "delivered"
		when o.deleted_at then "deleted"
		when o.refunded_at then "refunded"
		else "ordered"
	end as "ステータス",
	case
		when o.refund_id and not o.refunded_at then "refunding"
		when o.refunded_at then "refunded"
		when o.paid_at then "paid"
		else "unpaid"
	end as "決済ステータス",
	o.created_at as "予約日時",
	o.paid_at as "支払日時",
	o.delivered_at as "配送日時",
	o.canceled_at as "キャンセル日時",
	l.name as "抽選",
	o.total_amount as "合計金額",
	o.transaction_fee as "決済手数料",
	o.delivery_fee as "配送手数料",
	o.system_fee as "システム利用料",
	o.special_fee as "特別手数料",
	0 as "内手数料金額",
	o.refund_total_amount as "払戻合計金額",
	o.refund_transaction_fee as "払戻決済手数料",
	o.refund_delivery_fee as "払戻配送手数料",
	o.refund_system_fee as "払戻システム利用料",
	o.refund_special_fee as "払戻特別手数料",
	o.note as "メモ",
	o.special_fee_name as "特別手数料名",
	o.card_brand as "カードブランド",
	o.card_ahead_com_code as "仕向け先企業コード",
	o.card_ahead_com_name as "仕向け先企業名",
	o.issuing_start_at as "発券開始日時",
	o.issuing_end_at as "発券期限",
	o.payment_start_at as "支払開始日時",
	o.payment_due_at as "支払期限",
	so.billing_number as "SEJ払込票番号",
	so.exchange_number as "SEJ引換票番号",
	"メールマガジン受信可否",
	up.last_name as "姓",
	up.first_name as "名",
	up.last_name_kana as "姓(カナ)",
	up.first_name_kana as "名(カナ)",
	up.nick_name as "ニックネーム",
	up.sex as "性別",
	ms.name as "会員種別名",
	mg.name as "会員グループ名",
	uc.authz_identifier as "会員種別ID",
	sa.last_name as "配送先姓",
	sa.first_name as "配送先名",
	sa.last_name_kana as "配送先姓(カナ)",
	sa.first_name_kana as "配送先名(カナ)",
	sa.zip as "郵便番号",
	sa.country as "国",
	sa.prefecture as "都道府県",
	sa.city as "市区町村",
	sa.address_1 as "住所1",
	sa.address_2 as "住所2",
	case when 
		sa.tel_1 is not NULL then concat('="', sa.tel_1, '"') 
	else 
		'' 
	end as "電話番号1",
	case when 
		sa.tel_2 is not NULL then concat('="', sa.tel_2, '"') 
	else 
		'' 
	end as "電話番号2",
	case when 
		sa.fax is not NULL then concat('="', sa.fax, '"') 
	else 
		NULL 
	end as "FAX",
	sa.email_1 as "メールアドレス1",
	sa.email_2 as "メールアドレス2",
	pm.name as "決済方法",
	dm.name as "引取方法",
	e.title as "イベント",
	p.name as "公演",
	p.code as "公演コード",
	p.start_on "公演日",
	v.name as "会場",
	op.price as "商品単価",
	op.quantity as "商品個数",
	op.refund_price as "払戻商品単価",
	pt.name as "商品名",
	ssg.name as "販売区分",
	pti.name as "商品明細名",
	opi.price as "商品明細単価",
	opi.quantity as "商品明細個数",
	opi.refund_price as "払戻商品明細単価",
	opr.name as "発券作業者",
	s.name as "座席名",
	sh.name as "枠名"
from 
	`Order` o
join
	Performance p on o.performance_id = p.id
join
	Event e on p.event_id = e.id
join
	Venue v on p.id = v.performance_id
join 
	PaymentDeliveryMethodPair pdmp on o.payment_delivery_method_pair_id = pdmp.id
join
	SalesSegmentGroup ssg on pdmp.sales_segment_group_id = ssg.id
join
	PaymentMethod pm on pm.id = pdmp.payment_method_id
join
	DeliveryMethod dm on dm.id = pdmp.delivery_method_id
left join
	(
		LotEntry le
		join Lot l on l.id = le.lot_id
	) on o.order_no = le.entry_no
left join
	SejOrder so on o.order_no = so.order_no
left join
	UserProfile up on o.user_id = up.user_id
left join 
	MemberGroup mg on o.membergroup_id = mg.id
left join 
	Membership ms on o.membership_id = ms.id
left join
	UserCredential uc on o.user_id = uc.user_id
left join 
	ShippingAddress sa on o.shipping_address_id = sa.id
left join
	OrderedProduct op on o.id = op.order_id
left join
	Product pt on op.product_id = pt.id
left join
	OrderedProductItem opi on op.id = opi.ordered_product_id
left join 
	ProductItem pti on opi.product_item_id = pti.id
left join
	Stock st on pti.stock_id = st.id
left join
	StockHolder sh on st.stock_holder_id = sh.id
left join 
	TicketPrintHistory tph on o.id = tph.order_id and opi.id = tph.ordered_product_item_id
left join 
	Operator opr on tph.operator_id = opr.id 
left join
	OrderedProductItemToken opit on opit.ordered_product_item_id = opi.id
left join
	Seat s on opit.seat_id = s.id	
where 1
and p.id = {performance_id}
and o.deleted_at is NULL 
and o.canceled_at is NULL
and uc.deleted_at is NULL
and sa.deleted_at is NULL
"""

# helper
def encode_to_cp932(data):
    if not hasattr(data, "encode"):
        return str(data)
    try:
        return data.replace('\r\n', '').encode('cp932')
    except UnicodeEncodeError:
        print 'cannot encode character %s to cp932' % data
        if data is not None and len(data) > 1:
            return ''.join([encode_to_cp932(d) for d in data])
        else:
            return '?'

def main(performance_id=None, debug=False):
    if debug:
        ticketing_conn = connect(host='127.0.0.1', user='ticketing', passwd='ticketing', db='ticketing',
                                 port=3306, charset='utf8', cursorclass=cursors.DictCursor)
    else:
        ticketing_conn = connect(host='dbmain.standby.altr', user='ticketing_ro', passwd='ticketing', db='ticketing',
                                 port=3308, charset='utf8', cursorclass=cursors.DictCursor)

    try:
        ticketing_cur = ticketing_conn.cursor()
        ticketing_cur.execute(download_sql.format(performance_id=performance_id if performance_id else 0))
        columns = [column[0] for column in ticketing_cur.description]
        orders = ticketing_cur.fetchall()

        with open('nogizaka46_orders.csv', 'w') as f:
            writer = csv.writer(f, delimiter=',', quoting=csv.QUOTE_ALL)
            # write header
            writer.writerow([encode_to_cp932(column) for column in columns])
            for row in orders:
                values = [row[column] for column in columns]
                writer.writerow([encode_to_cp932(value) for value in values])
    finally:
        ticketing_conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=u"乃木坂46専用の大量予約ダウンロードツール")
    parser.add_argument('--performance_id', '-p', type=int, required=True, help=u"対象公演のIDを提供してください。")
    parser.add_argument('-d', '--debug', default=False, action='store_true')
    args = parser.parse_args()

    main(performance_id=args.performance_id, debug=args.debug)
