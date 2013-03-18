<!DOCTYPE html>
<html>
    <%include file="../common/_header.mako" args="title=u'楽天チケット[イベント詳細]'"/>
<body>

    % if form.genre.data:
        <a href="/genre?genre=${form.genre.data}&sub_genre=${form.sub_genre.data}" accesskey="0">[0]戻る</a>
    % else:
        <a href="/" accesskey="0">[0]戻る</a>
    % endif
    <a href="/" accesskey="9">[9]トップへ</a>
    <br/><br/>

    <a href="/">トップ</a> >> イベント詳細

<div class="line" style="background:#FFFFFF"><img src="../static/clear.gif" alt="" width="1" height="1" /></div>

<div style="background-image:url(../static/bg_bar.gif);background-color:#bf0000;
                        color: #ffffff" bgcolor="#bf0000" background="../static/bg_bar.gif">公演概要</div>

    ${form.event.data.title}<br/>

<%include file="_detail.mako" args="event=form.event.data, week=form.week.data, month_unit=form.month_unit.data,
                month_unit_keys=form.month_unit_keys.data, purchase_links=form.purchase_links.data,
                tickets=form.tickets.data, sales_start=form.sales_start.data, sales_end=form.sales_end.data" />

</body>
</html>
