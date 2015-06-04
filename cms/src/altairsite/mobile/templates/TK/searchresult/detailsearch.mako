<%inherit file="../common/_base.mako" />
<%namespace file="../common/tags_mobile.mako" name="m" />
<%block name="title">詳細検索</%block>
<%block name="fnavi">
% if form.genre.data:
  <a href="/genre?genre=${form.genre.data}&sub_genre=${form.sub_genre.data}" accesskey="0">[0]戻る</a><br />
% endif
[9]<a href="/" accesskey="9">トップへ</a><br />
</%block>
<%include file='_search_result_detail.mako' args="events=form.events.data
                ,word=form.word.data, num=form.num.data, page=form.page.data
                ,page_num=form.page_num.data, path=form.path.data, week=form.week.data
                ,genre=form.genre.data, sub_genre=form.sub_genre.data, area=form.area.data
                ,sale=form.sale.data, sales_segment=form.sales_segment.data, since_year=form.since_year.data
                ,since_month=form.since_month.data, since_day=form.since_day.data
                ,year=form.year.data, month=form.month.data, day=form.day.data, errors=form.errors"/>
<%include file='../detailsearch/_form.mako' args="form=form" />
