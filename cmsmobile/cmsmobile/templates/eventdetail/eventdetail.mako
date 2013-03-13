<!DOCTYPE html>
<html>
    <%include file="../common/_header.mako" args="title=u'楽天チケット[イベント詳細]'"/>
<body>

<span style="font-size: x-small">
    <a href="/">トップ</a> >> イベント詳細<p/>
</span>

<div style="font-size: medium">
    ${form.event.data.title}<br/>
</div>

<%include file="_detail.mako" args="event=form.event.data, week=form.week.data, month_unit=form.month_unit.data,
                month_unit_keys=form.month_unit_keys.data, purchase_links=form.purchase_links.data,
                tickets=form.tickets.data" />

</body>
</html>
