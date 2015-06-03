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

% if form.send.data == "Success":
    <div class="line" style="background:#FFFFFF"><img src="${request.mobile_static_url("altaircms:static/TK/mobile/clear.gif")}" alt="" width="1" height="1" /></div>
    <div style="color:#FF0000;">
        以下の内容で送信しました。<br/>
        受付の確認メールが自動で送信されます。<br/>
        もし受信されない場合は、ドメインの受信設定、迷惑メールフォルダ等をご確認ください。
    </div>
    <br/>
% elif form.send.data == "Failed":
    <div class="line" style="background:#FFFFFF"><img src="${request.mobile_static_url("altaircms:static/TK/mobile/clear.gif")}" alt="" width="1" height="1" /></div>
    <div style="color:#FF0000;">送信に失敗しました。</div>
    <br/>
% endif

<form action="/inquiry" method="POST">
    ${form.username.label}<br/>${form.username}<br/>
    ${disp_error(form.username.errors)}
    ${form.mail.label}<br/>${form.mail}<br/>
    ${disp_error(form.mail.errors)}
    ${form.num.label}<br/>
(ご予約済のチケットの受付番号が不明な場合は、こちらにお申込みの公演名、公演日時を入力してください)<br/>
    ${form.num}<br/>
    ${form.category.label}<br/>${form.category}<br/>
    ${disp_error(form.category.errors)}
    ${form.title.label}<br/>${form.title}<br/>
    ${disp_error(form.title.errors)}
    ${form.body.label}<br/>${form.body}<br/>
    ${disp_error(form.body.errors)}
    ※は必ず入力してください。
    % if form.send.data != "Success":
        <input type="submit" value="送信"/>
    % endif
</form>
