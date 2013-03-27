<!DOCTYPE html>
<html>
    <%include file='../common/_header.mako' args="title=u'楽天チケット[ホットワード]'"/>
<body>

<div style="background-image:url(../static/bg_bar.gif);background-color:#bf0000" bgcolor="#bf0000"><font color="#ffffff" size="3"><font color="#ffc0cb">■</font></font></div>

<div class="line" style="background:#FFFFFF"><img src="../static/clear.gif" alt="" width="1" height="1" /></div>

<a href="/">トップ</a>

    <%include file='../common/_search_result.mako' args="form=form, events=events" />

    <hr/>
    <%include file='../common/_footer.mako' />
</body>
</html>