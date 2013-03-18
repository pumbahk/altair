<%namespace file="cmsmobile:templates/common/helpers.html" name="h" />

<!DOCTYPE html>
<html>
<%include file="../common/_header.mako" args="title=u'楽天チケット[お問合せ]'"/>
<body>

    <a href="/">トップ</a> >> お問合せ

    <div class="line" style="background:#FFFFFF"><img src="../static/clear.gif" alt="" width="1" height="1" /></div>

    <div style="background-image:url(../static/bg_bar.gif);background-color:#bf0000;
                        color: #ffffff" bgcolor="#bf0000" background="../static/bg_bar.gif">お問合せ</div>

    お預かりするお客様の個人情報は、『個人情報保護方針』に基いて厳重に管理し、お客様の同意がない限りお問い合わせ・ご相談への対応以外には使用いたしません。<br/>
    <br/>

    個人情報保護方針は<a href="/privacy">こちら</a>をご確認ください。 フォームでお問い合わせ頂いたお客様には、基本的には返信メールにて回答させて頂いております。<br/>
    <br/>

    % if form.send.data:
        <div class="line" style="background:#FFFFFF"><img src="../static/clear.gif" alt="" width="1" height="1" /></div>
        <div style="color:#FF0000;">以下の内容で送信しました。</div>
    % endif

    <form action="/inquiry" method="POST">
        ${form.name.label}<br/>${form.name}<br/>
        ${form.mail.label}<br/>${form.mail}<br/>
        ${form.num.label}<br/>${form.num}<br/>
        ${form.category.label}<br/>${form.category}<br/>
        ${form.title.label}<br/>${form.title}<br/>
        ${form.body.label}<br/>${form.body}<br/>
        ※は必ず入力してください。
        <input type="submit" value="送信"/>
    </form>

    <%include file="../common/_footer.mako" />
</body>
</html>