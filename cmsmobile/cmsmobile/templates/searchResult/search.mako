<!DOCTYPE html>
<html>
    <%include file='../common/_header.mako' args="title=u'楽天チケット[検索]'"/>
<body>
    % if form.word.data:
        <a href="/">トップ</a> >> 検索 ${form.navi_area.data + u"で" if form.navi_area.data else ""}「${form.word.data}」を含む公演
    % else:
        <a href="/">トップ</a> >> 検索 「${form.navi_area.data if form.navi_area.data else ""}」
    % endif
    <br/><br/>

    <%include file='../common/_search_result.mako' args="events=form.events.data
                ,word=form.word.data, num=form.num.data, page=form.page.data
                ,page_num=form.page_num.data, path=form.path.data, week=form.week.data"/>

    <hr/>
    <%include file='../common/_search.mako' args="form=form"/>

    <%include file='../common/_footer.mako' />
</body>
</html>