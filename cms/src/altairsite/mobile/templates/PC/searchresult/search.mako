<%inherit file="../common/_base.mako" />
<%namespace file="../common/tags_mobile.mako" name="m" />
<%block name="title">
% if form.word.data:
    ${form.navi_area.data + u"で" if form.navi_area.data else ""}「${form.word.data}」を含む公演
% else:
    ${u"「" + form.navi_area.data + u"」" if form.navi_area.data else ""}
% endif
</%block>
<%block name="fnavi">
[9]<a href="/" accesskey="9">トップへ</a><br />
</%block>
<%include file='../common/_search_result.mako' args="events=form.events.data
            ,word=form.word.data, num=form.num.data, page=form.page.data
            ,page_num=form.page_num.data, path=form.path.data, week=form.week.data
            ,genre=0, sub_genre=0, area=form.area.data"/>
<%include file='../common/_search.mako' args="form=form, genre=0, sub_genre=0"/>
