SELECT
	id,
	CONCAT("'", tel_1, "'") AS tel_1
FROM
	ShippingAddress
LIMIT 1;