<!DOCTYPE html>
<html>
    <%include file='../common/_header.mako' args="title=u'詳細検索'"/>

    <div style="background-image:url(../static/bg_bar.gif);background-color:#bf0000" bgcolor="#bf0000"><font color="#ffffff" size="3"><font color="#ffc0cb">■</font>詳細検索</font></div>

    <div class="line" style="background:#FFFFFF"><img src="../static/clear.gif" alt="" width="1" height="1" /></div>

    % if form.genre.data:
        <a href="/genre?genre=${form.genre.data}&sub_genre=${form.sub_genre.data}" accesskey="0">[0]戻る</a>
    % else:
        <a href="/" accesskey="0">[0]戻る</a>
    % endif
    <a href="/" accesskey="9">[9]トップへ</a>
    <br/><br/>

    <a href="/">トップ</a> >> 詳細検索

    <%include file='_search_result_detail.mako' args="events=form.events.data
                    ,word=form.word.data, num=form.num.data, page=form.page.data
                    ,page_num=form.page_num.data, path=form.path.data, week=form.week.data
                    ,genre=form.genre.data, sub_genre=form.sub_genre.data, area=form.area.data
                    ,sale=form.sale.data, sales_segment=form.sales_segment.data, since_year=form.since_year.data
                    ,since_month=form.since_month.data, since_day=form.since_day.data
                    ,year=form.year.data, month=form.month.data, day=form.day.data, errors=form.errors"/>

    <div class="line" style="background:#FFFFFF"><img src="../static/clear.gif" alt="" width="1" height="1" /></div>

    <div style="background-image:url(../static/bg_bar.gif);background-color:#bf0000" bgcolor="#bf0000"><font color="#ffffff" size="3"><font color="#ffbf00">■</font>詳細検索</font></div>

    <div class="line" style="background:#FFFFFF"><img src="../static/clear.gif" alt="" width="1" height="1" /></div>

    <%include file='../detailsearch/_form.mako' args="form=form" />

    <%include file='../common/_footer.mako' />
</body>
</html>