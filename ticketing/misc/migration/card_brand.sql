UPDATE `multicheckout_request_card` SET card_brand=(CASE WHEN CardNo LIKE '34%' OR CardNo LIKE '37%' THEN 'AMEX' WHEN CardNo LIKE '30%' OR CardNo LIKE '36%' OR CardNo LIKE '38%' OR CardNo LIKE '39%' THEN 'DINERS' WHEN CardNo LIKE '5%' THEN 'MASTER' WHEN CardNo LIKE '4%' THEN 'VISA' WHEN CardNo LIKE '35%' THEN 'JCB' WHEN CardNO LIKE '62%' THEN 'UNIONPAY' END);
-- ダミーの multicheckout_request_card を作る (card_brand のキープ用)
INSERT INTO `multicheckout_request_card` (ItemCd, ItemName, OrderYMD, SalesAmount, TaxCarriage, ClientName, MailAddress, FreeData, card_brand) SELECT '120', CONCAT(Organization.name, ' ', Performance.id), DATE_FORMAT(`Order`.created_at, '%Y%m%d'), `Order`.total_amount, 0, CONCAT(ShippingAddress.last_name, ShippingAddress.first_name), ShippingAddress.email_1, `multicheckout_response_card`.OrderNo, `Order`.card_brand FROM `Order` JOIN `Performance` ON `Order`.performance_id=`Performance`.id JOIN Organization ON `Order`.organization_id=`Organization`.id JOIN `multicheckout_response_card` ON SUBSTR(`multicheckout_response_card`.OrderNo, 1, 12)=`Order`.order_no JOIN `ShippingAddress` ON `ShippingAddress`.id=`Order`.shipping_address_id WHERE `Order`.branch_no=1 AND `multicheckout_response_card`.request_id IS NULL;
-- multicheckout_response_card と multicheckout_request_card の関連付け
UPDATE `multicheckout_response_card` JOIN `multicheckout_request_card` ON `multicheckout_request_card`.FreeData=`multicheckout_response_card`.OrderNo SET `multicheckout_response_card`.request_id=`multicheckout_request_card`.id WHERE `multicheckout_response_card`.request_id IS NULL;