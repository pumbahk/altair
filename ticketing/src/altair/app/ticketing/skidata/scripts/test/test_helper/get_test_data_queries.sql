# testdata rule demo: SELECT '' as 'table_name_XXXX', XXXX.* FROM XXXX;
SELECT '' as 'table_name_Order',
       O.*,
       '' as 'table_name_Organization',
       Organization.*,
       '' as 'table_name_OrganizationSetting',
       OS.*,
       '' as 'table_name_Performance',
       P.*,
       '' as 'table_name_Event',
       E.*,
       '' as 'table_name_EventSetting',
       ES.*,
       '' as 'table_name_OrderedProduct',
       OP.*,
       '' as 'table_name_Product',
       P2.*,
       '' as 'table_name_SalesSegment',
       SS.*,
       '' as 'table_name_SalesSegmentGroup',
       SSG.*,
       '' as 'table_name_OrderedProductItem',
       OPI.*,
       '' as 'table_name_ProductItem',
       PI.*,
       '' as 'table_name_Stock',
       S.*,
       '' as 'table_name_StockType',
       ST.*,
       '' as 'table_name_OrderedProductItemToken',
       OPIT.*,
       '' as 'table_name_Seat',
       S2.*,
       '' as 'table_name_SkidataBarcode',
       SB.*
FROM `Order` O
    join Organization on O.organization_id = Organization.id and Organization.deleted_at is null
    join OrganizationSetting OS on Organization.id = OS.organization_id and OS.deleted_at is null
    join Performance P on O.performance_id = P.id and p.deleted_at is null
    join Event E on P.event_id = E.id and E.deleted_at is null
    join EventSetting ES on E.id = ES.event_id and ES.deleted_at is null
    join OrderedProduct OP on O.id = OP.order_id and OP.deleted_at is null
    join Product P2 on OP.product_id = P2.id and P2.deleted_at is null
    join SalesSegment SS on P2.sales_segment_id = SS.id and SS.deleted_at is null
    join SalesSegmentGroup SSG on SS.sales_segment_group_id = SSG.id and SSG.deleted_at is null
    join OrderedProductItem OPI on OP.id = OPI.ordered_product_id and OPI.deleted_at is null
    join ProductItem PI on OPI.product_item_id = PI.id and PI.deleted_at is null
    join Stock S on PI.stock_id = S.id and S.deleted_at is null
    join StockType ST on S.stock_type_id = ST.id and ST.deleted_at is null
    join OrderedProductItemToken OPIT on OPI.id = OPIT.ordered_product_item_id and OPIT.deleted_at is null
    left join Seat S2 on OPIT.seat_id = S2.id and S2.deleted_at is null
    join SkidataBarcode SB on OPIT.id = SB.ordered_product_item_token_id and SB.deleted_at is null
WHERE OS.enable_skidata = 1 and ES.enable_skidata =1
and SB.canceled_at is null and SB.sent_at is null
and O.canceled_at is null and O.refunded_at is null and O.paid_at is not null and O.deleted_at is null
and P.open_on between '2019-12-03 09:29:01' and '2022-08-29 00:00:00';


SELECT '' as 'table_name_SkidataProperty',
       SP.*,
       '' as 'table_name_SkidataPropertyEntry',
       SPE.*
       from SkidataProperty SP
    join SkidataPropertyEntry SPE on SP.id = SPE.skidata_property_id
WHERE SP.deleted_at is null and SPE.deleted_at is null;
