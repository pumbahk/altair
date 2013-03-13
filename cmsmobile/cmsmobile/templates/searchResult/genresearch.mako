<!DOCTYPE html>
<html>
    <%include file='../common/_header.mako' args="title=u'検索結果'"/>
<body>
    <%include file='_navigation.mako' args="word=form.word.data, navi_genre=form.navi_genre.data,
                                               navi_sub=form.navi_sub_genre.data, area=form.area.data" />

    <%include file='../common/_search_result.mako' args="events=form.events.data
                      ,word=form.word.data, num=form.num.data, page=form.page.data
                      ,page_num=form.page_num.data, path=form.path.data, week=form.week.data"/>

    <%include file='../common/_search.mako' args="path='/search', genre='', subgenre=''"/>

    <%include file='../common/_footer.mako' />
</body>
</html>