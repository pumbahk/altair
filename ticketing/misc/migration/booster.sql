BEGIN;

INSERT INTO OrderAttribute
    (
        order_id,
        name,
        value,
        created_at,
        updated_at,
        deleted_at
    )
    SELECT
        OrderedProduct.order_id,
        CASE
            WHEN OrderedProductAttribute.name='extra.coupon'
                THEN 'coupon'
            WHEN OrderedProductAttribute.name='extra.mail_permission'
                THEN 'mail_permission'
            WHEN OrderedProductAttribute.name='extra.motivation'
                THEN 'motivation'
            WHEN OrderedProductAttribute.name='extra.num_times_at_venue'
                THEN 'num_times_at_venue'
            WHEN OrderedProductAttribute.name='extra.official_ball'
                THEN 'official_ball'
            WHEN OrderedProductAttribute.name='extra.publicity'
                THEN 'publicity'
            WHEN OrderedProductAttribute.name='extra.t_shirts_size'
                THEN 't_shirts_size'
            WHEN OrderedProductAttribute.name='extra.parent_first_name'
                THEN 'parent_first_name'
            WHEN OrderedProductAttribute.name='extra.parent_first_name_kana'
                THEN 'parent_first_name_kana'
            WHEN OrderedProductAttribute.name='extra.parent_last_name'
                THEN 'parent_last_name'
            WHEN OrderedProductAttribute.name='extra.parent_last_name_kana'
                THEN 'parent_last_name_kana'
            WHEN OrderedProductAttribute.name='extra.relationship'
                THEN 'relationship'
            ELSE
                OrderedProductAttribute.name
        END,
        CASE
            WHEN OrderedProductAttribute.name='sex'
                THEN CASE
                    WHEN OrderedProductAttribute.value='1'
                        THEN 'male'
                    WHEN OrderedProductAttribute.value='2'
                        THEN 'female'
                    ELSE
                        OrderedProductAttribute.value
                END
            WHEN OrderedProductAttribute.name='sex'
                THEN CASE
                    WHEN OrderedProductAttribute.value='1'
                        THEN 'male'
                    WHEN OrderedProductAttribute.value='2'
                        THEN 'female'
                    ELSE
                        OrderedProductAttribute.value
                END
            ELSE
                OrderedProductAttribute.value
        END,
        OrderedProductAttribute.created_at,
        OrderedProductAttribute.updated_at, 
        OrderedProductAttribute.deleted_at
    FROM
        OrderedProduct JOIN OrderedProductItem ON OrderedProduct.id=OrderedProductItem.ordered_product_id
        JOIN OrderedProductAttribute ON OrderedProductItem.id=OrderedProductAttribute.ordered_product_item_id
    WHERE
        OrderedProductAttribute.name NOT IN ('year', 'month', 'day');


INSERT INTO OrderAttribute
    (
        order_id,
        name,
        value,
        created_at,
        updated_at,
        deleted_at
    )
    SELECT
        OrderedProduct.order_id,
        'birthday',
        DATE(CONCAT(
            (SELECT value FROM OrderedProductAttribute _ WHERE _.ordered_product_item_id=OrderedProductItem.id AND _.name='year'), '-',
            (SELECT value FROM OrderedProductAttribute _ WHERE _.ordered_product_item_id=OrderedProductItem.id AND _.name='month'), '-',
            (SELECT value FROM OrderedProductAttribute _ WHERE _.ordered_product_item_id=OrderedProductItem.id AND _.name='day')
        )),
        OrderedProductAttribute.created_at,
        OrderedProductAttribute.updated_at, 
        OrderedProductAttribute.deleted_at
    FROM
        OrderedProduct JOIN OrderedProductItem ON OrderedProduct.id=OrderedProductItem.ordered_product_id
        JOIN OrderedProductAttribute ON OrderedProductItem.id=OrderedProductAttribute.ordered_product_item_id
    WHERE
        OrderedProductAttribute.name='year';

UPDATE `OrderedProductAttribute` SET deleted_at=NOW();
