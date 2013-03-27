<!DOCTYPE html>
<html>
    <%include file='../common/_header.mako' args="title=u'楽天チケット[ホットワード]'"/>
<body>

    <div style="background-image:url(../static/bg_bar.gif);background-color:#bf0000" bgcolor="#bf0000"><font color="#ffffff" size="3"><font color="#ffc0cb">■</font>ホットワード</font></div>

    <div class="line" style="background:#FFFFFF"><img src="../static/clear.gif" alt="" width="1" height="1" /></div>

    % if form.genre.data:
        <a href="/genre?genre=${form.genre.data}&sub_genre=${form.sub_genre.data}" accesskey="0">[0]戻る</a>
    % else:
        <a href="/" accesskey="0">[0]戻る</a>
    % endif
    <a href="/" accesskey="9">[9]トップへ</a>
    <br/><br/>

    <a href="/">トップ</a> >> 「${form.navi_hotword.data.name}」に関連する公演<br/><br/>

    <%include file='_search_result_hotword.mako' args="events=form.events.data
                ,word=form.word.data, num=form.num.data, page=form.page.data,id=form.id.data
                ,page_num=form.page_num.data, path=form.path.data, week=form.week.data
                ,genre=form.genre.data, sub_genre=form.sub_genre.data, area=form.area.data"/>

    <%include file='../common/_footer.mako' />
</body>
</html>