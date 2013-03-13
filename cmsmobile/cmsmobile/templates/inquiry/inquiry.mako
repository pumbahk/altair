<%namespace file="cmsmobile:templates/common/helpers.html" name="h" />

<!DOCTYPE html>
<html>
<%include file="../common/_header.mako" args="title=u'楽天チケット[お問合せ]'"/>
<body>

    <div style="font-size: x-small">
        <a href="/">トップ</a> >> お問合せ
    </div>

    <div class="line" style="background:#FFFFFF"><img src="../static/clear.gif" alt="" width="1" height="1" /></div>

    <div style="background-image:url(../static/bg_bar.gif);background-color:#bf0000;font-size: medium;
                        color: #ffffff" bgcolor="#bf0000" background="../static/bg_bar.gif">お問合せ</div>

    <div style="font-size: x-small">お預かりするお客様の個人情報は、『個人情報保護方針』に基いて厳重に管理し、お客様の同意がない限りお問い合わせ・ご相談への対応以外には使用いたしません。</div>

    <div style="font-size: x-small">個人情報保護方針は<a href="/privacy">こちら</a>をご確認ください。 フォームでお問い合わせ頂いたお客様には、基本的には返信メールにて回答させて頂いております。</div>

    % if form.send.data:
        <div class="line" style="background:#FFFFFF"><img src="../static/clear.gif" alt="" width="1" height="1" /></div>
        <div style="color:#FF0000;">以下の内容で送信しました。</div>
    % endif

    <form action="/inquiry" method="POST">
        <fieldset>
            <div style="font-size: x-small">
                ${h.form_item(form.name, style="font-size: x-small")}<br/>
                ${h.form_item(form.mail, style="font-size: x-small")}<br/>
                ${h.form_item(form.num, style="font-size: x-small")}
                <div style="font-size: x-small">予約受付番号をお持ちの場合入力してください。</div>
                ${h.form_item(form.category, style="font-size: x-small")}<br/>
                ${h.form_item(form.title, style="font-size: x-small")}<br/>
                ${h.form_item(form.body, style="font-size: x-small")}<br/>
            </div>
        </fieldset>
        <div style="font-size: x-small">※は必ず入力してください。</div>
        <input type="submit" value="送信" style="font-size: x-small"/>
    </form>

    <%include file="../common/_footer.mako" />
</body>
</html>