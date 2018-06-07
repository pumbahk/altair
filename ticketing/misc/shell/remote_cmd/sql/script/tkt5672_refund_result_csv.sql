SELECT
	`SejRefundTicket`.order_no AS order_no,
	`StockType`.name AS stock_type_name,
	`Product`.name AS product_name,
	`ProductItem`.name AS product_item_name,
	`SejRefundTicket`.sent_at AS sent_at,
	`SejRefundTicket`.refunded_at AS refunded_at,
	`SejRefundTicket`.ticket_barcode_number AS barcode_number,
	`SejRefundTicket`.refund_ticket_amount AS refund_ticket_amount,
	`SejRefundTicket`.refund_other_amount AS refund_other_amount,
	`SejRefundTicket`.status AS status
FROM
	`Order`
INNER JOIN `SejRefundTicket` ON
	`SejRefundTicket`.order_no = `Order`.order_no
	AND `SejRefundTicket`.deleted_at IS NULL
	AND `SejRefundTicket`.deleted_at IS NULL
	AND `SejRefundTicket`.deleted_at IS NULL
INNER JOIN `SejTicket` ON
	`SejTicket`.barcode_number = `SejRefundTicket`.ticket_barcode_number
	AND `SejTicket`.deleted_at IS NULL
	AND `SejTicket`.deleted_at IS NULL
	AND `SejTicket`.deleted_at IS NULL
INNER JOIN `ProductItem` ON
	`ProductItem`.id = `SejTicket`.product_item_id
	AND `ProductItem`.deleted_at IS NULL
	AND `ProductItem`.deleted_at IS NULL
	AND `ProductItem`.deleted_at IS NULL
INNER JOIN `Product` ON
	`Product`.id = `ProductItem`.product_id
	AND `Product`.deleted_at IS NULL
	AND `Product`.deleted_at IS NULL
	AND `Product`.deleted_at IS NULL
INNER JOIN `Stock` ON
	`Stock`.id = `ProductItem`.stock_id
	AND `Stock`.deleted_at IS NULL
	AND `Stock`.deleted_at IS NULL
	AND `Stock`.deleted_at IS NULL
INNER JOIN `StockType` ON
	`StockType`.id = `Stock`.stock_type_id
	AND `StockType`.deleted_at IS NULL
	AND `StockType`.deleted_at IS NULL
	AND `StockType`.deleted_at IS NULL
WHERE
	`Order`.refund_id = 1462
	AND `Order`.deleted_at IS NULL;