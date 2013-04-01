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
お預かりするお客様の個人情報は、『個人情報保護方針』に基いて厳重に管理し、お客様の同意がない限りお問い合わせ・ご相談への対応以外には使用いたしません。<br />
<br/>
個人情報保護方針は<a href="/privacy">こちら</a>をご確認ください。 フォームでお問い合わせ頂いたお客様には、基本的には返信メールにて回答させて頂いております。<br/>
% if form.send.data == "Success":
    <div class="line" style="background:#FFFFFF"><img src="/static/mobile/clear.gif" alt="" width="1" height="1" /></div>
    <div style="color:#FF0000;">以下の内容で送信しました。</div>
    <br/>
% elif form.send.data == "Failed":
    <div class="line" style="background:#FFFFFF"><img src="/static/mobile/clear.gif" alt="" width="1" height="1" /></div>
    <div style="color:#FF0000;">送信に失敗しました。</div>
    <br/>
% endif

<form action="/inquiry" method="POST">
    ${form.name.label}<br/>${form.name}<br/>
    ${disp_error(form.name.errors)}
    ${form.mail.label}<br/>${form.mail}<br/>
    ${disp_error(form.mail.errors)}
    ${form.num.label}<br/>${form.num}<br/>
    ${form.category.label}<br/>${form.category}<br/>
    ${disp_error(form.category.errors)}
    ${form.title.label}<br/>${form.title}<br/>
    ${disp_error(form.title.errors)}
    ${form.body.label}<br/>${form.body}<br/>
    ${disp_error(form.body.errors)}
    ※は必ず入力してください。
    <input type="submit" value="送信"/>
</form>
