<%namespace file="cmsmobile:templates/common/helpers.html" name="h" />

<!DOCTYPE html>
<html>
<%include file="../common/_header.mako" args="title=u'楽天チケット[お問合せ]'"/>
<body>

    <a href="/">トップ</a> >> お問合せ
    <p/>
    お預かりするお客様の個人情報は、『個人情報保護方針』に基いて厳重に管理し、お客様の同意がない限りお問い合わせ・ご相談への対応以外には使用いたしません。
    <p/>

    個人情報保護方針は<a href="/privacy">こちら</a>をご確認ください。 フォームでお問い合わせ頂いたお客様には、基本的には返信メールにて回答させて頂いております。
    <p/>

    % if form.send.data:
        <span style="color:#FF0000;">以下の内容で送信しました。</span><p/>
    % endif

    <form action="/inquiry" method="POST">
        <fieldset>
            ${h.form_item(form.name)}<p/>
            ${h.form_item(form.mail)}<p/>
            ${h.form_item(form.num)}
            予約受付番号をお持ちの場合入力してください。<p/>
            ${h.form_item(form.category)}<p/>
            ${h.form_item(form.title)}<p/>
            ${h.form_item(form.body)}<p/>
        </fieldset>
        ※は必ず入力してください。
        <input type="submit" value="送信"/>
    </form>

    <%include file="../common/_footer.mako" />
</body>
</html>