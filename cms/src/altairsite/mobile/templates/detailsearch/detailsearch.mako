<!DOCTYPE html>
<html>
    <%include file='../common/_header.mako' args="title=u'楽天チケット[詳細検索]'"/>

<body>

    <div style="background-image:url(/static/mobile/bg_bar.gif);background-color:#bf0000" bgcolor="#bf0000"><font color="#ffffff" size="3"><font color="#ffc0cb">■</font>詳細検索</font></div>

    <div class="line" style="background:#FFFFFF"><img src="/static/mobile/clear.gif" alt="" width="1" height="1" /></div>

    % if form.genre.data:
        <a href="/genre?genre=${form.genre.data}&sub_genre=${form.sub_genre.data}" accesskey="0">[0]戻る</a>
    % else:
        <a href="/" accesskey="0">[0]戻る</a>
    % endif
    <a href="/" accesskey="9">[9]トップへ</a>
    <br/><br/>

    <a href="/">トップ</a> >> 詳細検索<br/><br/>

    <div class="line" style="background:#FFFFFF"><img src="/static/mobile/clear.gif" alt="" width="1" height="1" /></div>

    <div style="background-image:url(/static/mobile/bg_bar.gif);background-color:#bf0000" bgcolor="#bf0000"><font color="#ffffff" size="3"><font color="#ffbf00">■</font>詳細検索</font></div>

    <div class="line" style="background:#FFFFFF"><img src="/static/mobile/clear.gif" alt="" width="1" height="1" /></div>


<%include file='./_form.mako' args="form=form" />

    <%include file='../common/_footer.mako' />
</body>
</html>