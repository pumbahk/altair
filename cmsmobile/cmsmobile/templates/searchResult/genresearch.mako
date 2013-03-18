<!DOCTYPE html>
<html>
    <%include file='../common/_header.mako' args="title=u'検索結果'"/>
<body>

    <a href="/genre?genre=${form.genre.data}&sub_genre=${form.sub_genre.data}" accesskey="0">[0]戻る</a>
    <a href="/" accesskey="9">[9]トップへ</a>
    <br/><br/>

    <%include file='_navigation.mako' args="word=form.word.data, navi_genre=form.navi_genre.data,
                                               navi_sub=form.navi_sub_genre.data, area=form.area.data" />

    <%include file='../common/_search_result.mako' args="events=form.events.data
                      ,word=form.word.data, num=form.num.data, page=form.page.data
                      ,page_num=form.page_num.data, path=form.path.data, week=form.week.data
                      ,genre=form.genre.data, sub_genre=form.sub_genre.data"/>

    <hr/>
    <%include file='../common/_search.mako' args="path='/search', genre=form.genre.data, sub_genre=form.sub_genre.data"/>

    <%include file='../common/_footer.mako' />
</body>
</html>