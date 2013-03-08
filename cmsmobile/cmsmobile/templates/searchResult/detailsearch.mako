<!DOCTYPE html>
<html>
    <%include file='../common/_header.mako' args="title=u'詳細検索'"/>

<body>
<a href="/">トップ</a> >> 詳細検索<p/>

<p/>

<%include file='../common/_search_result.mako' args="events=form.events.data
                    ,word=form.word.data, num=form.num.data, page=form.page.data
                    ,page_num=form.page_num.data, path=form.path.data, week=form.week.data"/>

<%include file='../detailsearch/_form.mako' args="form=form" />

<hr/>
    <%include file='../common/_footer.mako' />
</body>
</html>