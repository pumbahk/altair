<!DOCTYPE html>
<html>
    <%include file='../common/_header.mako' args="title=u'楽天チケット[ホットワード]'"/>
<body>
    % if form.genre.data:
        <a href="/genre?genre=${form.genre.data}&sub_genre=${form.sub_genre.data}" accesskey="0">[0]戻る</a>
    % else:
        <a href="/" accesskey="0">[0]戻る</a>
    % endif
    <a href="/" accesskey="9">[9]トップへ</a>
    <br/><br/>

    <a href="/">トップ</a> >> 「${form.navi_hotword.data.name}」を含む公演<br/><br/>

    <%include file='../common/_search_result.mako' args="events=form.events.data
                ,word=form.word.data, num=form.num.data, page=form.page.data
                ,page_num=form.page_num.data, path=form.path.data, week=form.week.data
                ,genre=form.genre.data, sub_genre=form.sub_genre.data, area=form.area.data"/>

    <%include file='../common/_footer.mako' />
</body>
</html>