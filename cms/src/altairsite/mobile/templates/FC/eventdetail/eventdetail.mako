<%inherit file="../common/_base.mako" />
<%namespace file="../common/tags_mobile.mako" name="m" />
<%block name="title">${form.event.data.title}</%block>
<%block name="fnavi">
[9]<a href="/" accesskey="9">トップへ</a><br />
</%block>
<%include file="_detail.mako" args="event=form.event.data, week=form.week.data, month_unit=form.month_unit.data, month_unit_keys=form.month_unit_keys.data, purchase_links=form.purchase_links.data, tickets=form.tickets.data, sales_start=form.sales_start.data, sales_end=form.sales_end.data, helper=helper, event_helper=event_helper" />
