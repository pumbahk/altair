<%inherit file="../common/_base.mako" />
<%namespace file="../common/tags_mobile.mako" name="m" />
<%block name="title">詳細検索</%block>
<%
breadcrumbs = []

breadcrumbs.append(
  (request.mobile_route_path('genre', _query=dict(genre=form.navi_genre.data.id)),
   form.navi_genre.data.label))
if form.navi_sub_genre.data:
  breadcrumbs.append(
    (request.mobile_route_path('genre', _query=dict(genre=form.navi_genre.data.id, sub_genre=form.navi_sub_genre.data.id)),
     form.navi_sub_genre.data.label))
if form.navi_area.data:
  breadcrumbs.append(
    (request.mobile_route_path('genresearch', _query=dict(genre=form.navi_genre.data.id, sub_genre=form.navi_sub_genre.data and form.navi_sub_genre.data.id, area=form.area.data)), u'地域「%s」' % form.navi_area.data))
if form.word.data:
  breadcrumbs.append(
    (request.mobile_route_path('genresearch', _query=dict(genre=form.navi_genre.data.id, sub_genre=form.navi_sub_genre.data and form.navi_sub_genre.data.id, area=form.area.data, word=form.word.data)), u'「%s」を含む' % form.word.data))

self.breadcrumbs = breadcrumbs
%>
<%m:header>検索条件</%m:header>
% for i in range(len(breadcrumbs)):
<% breadcrumb = breadcrumbs[i] %>
% if i + 1 < len(breadcrumbs):
<a href="${breadcrumb[0]}">${breadcrumb[1]}</a> &gt;
% else:
${breadcrumb[1]}
% endif
% endfor
<br />
<hr />
<%block name="fnavi">
[9]<a href="/" accesskey="9">トップへ</a><br />
</%block>
<%include file='../common/_search_result.mako' args="events=form.events.data
                  ,word=form.word.data, num=form.num.data, page=form.page.data
                  ,page_num=form.page_num.data, path=form.path.data, week=form.week.data
                  ,genre=form.genre.data, sub_genre=form.sub_genre.data, area=form.area.data"/>

<%include file='../common/_search.mako' args="path='/search', genre=form.genre.data, sub_genre=form.sub_genre.data"/>
