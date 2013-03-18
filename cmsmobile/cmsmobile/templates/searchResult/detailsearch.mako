<!DOCTYPE html>
<html>
    <%include file='../common/_header.mako' args="title=u'詳細検索'"/>

    % if form.genre.data:
        <a href="/genre?genre=${form.genre.data}&sub_genre=${form.sub_genre.data}" accesskey="0">[0]戻る</a>
    % else:
        <a href="/" accesskey="0">[0]戻る</a>
    % endif
    <a href="/" accesskey="9">[9]トップへ</a>
    <br/><br/>

    <a href="/">トップ</a> >> 詳細検索

    <%include file='../common/_search_result.mako' args="events=form.events.data
                    ,word=form.word.data, num=form.num.data, page=form.page.data
                    ,page_num=form.page_num.data, path=form.path.data, week=form.week.data
                    ,genre=form.genre.data, sub_genre=form.sub_genre.data"/>

<%include file='../detailsearch/_form.mako' args="form=form" />

    <%include file='../common/_footer.mako' />
</body>
</html>