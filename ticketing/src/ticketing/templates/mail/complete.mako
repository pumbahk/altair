${name}　様


以下のご注文の受付が完了しました。ご利用ありがとうございました。

-----
■お名前カナ
${name_kana}
■電話番号（携帯）
${tel_no if tel_no else ''}
■電話番号（自宅）
${tel2_no if tel2_no else ''}
■メールアドレス
${email}

-----
■受付番号
${order_no}
予約内容確認の際などに必要です。必ずお控え下さい。

■受付日
${order_datetime}

-----
${performance_name}

■購入いただいた座席

■商品代金
%for ordered_product in order_items:
${ordered_product.product.name} ${h.format_currency(ordered_product.product.price)}
%endfor

■サービス利用料・手数料
システム利用料： ${h.format_currency(system_fee)}
セブン-イレブン決済手数料：${h.format_currency(transaction_fee)} 円
%if delivery_fee:
配送手数料：${h.format_currency(delivery_fee)}
%endif

■合計金額
${h.format_currency(order_total_amount)}

-----
■お支払
お支払方法： ${payment_method_name}
${h.render_payment_finished_mail_viewlet(request, order)}
-----
■お受取
お受取方法： ${delivery_method_name}
${h.render_delivery_finished_mail_viewlet(request, order)}

※本メールは自動配信メールとなり、こちらに返信されても返答はいたしかねます。

※営利目的としたチケットの転売は禁止となっております。

----

仙台89ERS（ナイナーズチケット）　チケット事務局

電話番号：022-215-8138　（平日09：00~18：00）
