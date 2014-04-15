<%inherit file="../common/_base.mako" />
<%namespace file="../common/tags_mobile.mako" name="m" />
<%block name="title">「${form.mobile_tag.data.label}」に関連する公演</%block>
<%block name="fnavi">
% if form.genre.data != "0":
    <a href="/genre?genre=${form.genre.data}&sub_genre=${form.sub_genre.data}" accesskey="0">[0]戻る</a><br />
% endif
[9]<a href="/" accesskey="9">トップへ</a>
</%block>
<%include file='_search_result_mobiletag.mako' args="events=form.events.data
              ,word=form.word.data, num=form.num.data, page=form.page.data,mobile_tag=form.mobile_tag.data
              ,page_num=form.page_num.data, path=form.path.data, week=form.week.data
              ,genre=form.genre.data, sub_genre=form.sub_genre.data, area=form.area.data"/>
