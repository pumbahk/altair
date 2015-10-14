<%inherit file="../common/_base.mako" />
<%namespace file="../common/tags_mobile.mako" name="m" />
<%def name="disp_error(errors)">
    % if errors:
        % for error in errors:
            <div style="color:#FF0000;">${error}</div>
        % endfor
    % endif
</%def>
<%block name="title">お問合せ</%block>
<%block name="fnavi">
[9]<a href="/" accesskey="9">トップへ</a><br />
</%block>

お預かりするお客様の個人情報は、『個人情報保護方針』に基いて厳重に管理し、お客様の同意がない限りお問い合わせ・ご相談への対応以外には使用いたしません。<br/>
<br/>
個人情報保護方針は<a href="/privacy">こちら</a>をご確認ください。<br/>
フォームでお問い合わせ頂いたお客様には、基本的に返信メールにて、3営業日内に回答させて頂いております。<br/>
(土日祝は原則対応いたしかねます)<br/>
<br/>
※携帯電話等の受信設定でドメイン指定受信を設定している方は、「@ticket.rakuten.co.jp」からのメールを受信できるように設定してください。<br/>
<br/>

［ご注意］<br/>
公演の内容、発売の時期や方法については、各公演ページをご覧ください。<br/>
お申込み手続きの依頼や、購入されたチケットの変更・キャンセルの依頼についてはお受けできません。<br/>
システムに関する問合せはお受けできません。<br/>
「<a href="http://ticket.rakuten.co.jp/faq">よくある質問</a>」に掲載している内容については、お返事をお送りできない場合があります。<br/>
問合せの前によくご確認ください。<br/><br/>

% if form.send.data == "Success":
    <div class="line" style="background:#FFFFFF"><img src="${request.mobile_static_url("altaircms:static/RT/mobile/clear.gif")}" alt="" width="1" height="1" /></div>
    <div style="color:#FF0000;">
        以下の内容で送信しました。<br/>
        受付の確認メールが自動で送信されます。<br/>
        もし受信されない場合は、ドメインの受信設定、迷惑メールフォルダ等をご確認ください。
    </div>
    <br/>
% elif form.send.data == "Failed":
    <div class="line" style="background:#FFFFFF"><img src="${request.mobile_static_url("altaircms:static/RT/mobile/clear.gif")}" alt="" width="1" height="1" /></div>
    <div style="color:#FF0000;">送信に失敗しました。</div>
    <br/>
% endif

<form action="/inquiry" method="POST">
    お名前<br/>
    漢字<span style="color:#FF0000;">※</span><br/>${form.username}<br/>
    ${disp_error(form.username.errors)}
    カナ<span style="color:#FF0000;">※</span><br/>${form.username_kana}<br/>
    ${disp_error(form.username_kana.errors)}
    ${form.mail.label}<span style="color:#FF0000;">※</span><br/>${form.mail}<br/>
    ${disp_error(form.mail.errors)}
    〒郵便番号<span style="color:#FF0000;">※</span><br/>${form.zip_no}<br/>
    ${disp_error(form.zip_no.errors)}
    ${form.address.label}<span style="color:#FF0000;">※</span><br/>${form.address}<br/>
    ${disp_error(form.address.errors)}
    ${form.tel.label}<span style="color:#FF0000;">※</span><br/>${form.tel}<br/>
    ${disp_error(form.tel.errors)}
    ${form.num.label}<span style="color:#FF0000;">※</span><br/>
(ご予約済のチケットの受付番号が不明な場合は、こちらにお申込みの公演名、公演日時を入力してください)<br/>
    ${form.num}<br/>
    ${form.category.label}<span style="color:#FF0000;">※</span><br/>${form.category}<br/>
    ${disp_error(form.category.errors)}
    ${form.title.label}<span style="color:#FF0000;">※</span><br/>${form.title}<br/>
    ${disp_error(form.title.errors)}
    ${form.body.label}(具体的に記載してください)<span style="color:#FF0000;">※</span><br/>${form.body}<br/>
    ${disp_error(form.body.errors)}
    <span style="color:#FF0000;">※</span>は必ず入力してください。
    % if form.send.data != "Success":
        <input type="submit" value="送信"/>
    % endif
</form>
