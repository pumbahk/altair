<%inherit file="../common/_base.mako" />
<%namespace file="../common/tags_mobile.mako" name="m" />
<%block name="title">詳細検索</%block>
<%block name="fnavi">
% if form.genre.data:
<a href="/genre?genre=${form.genre.data}&sub_genre=${form.sub_genre.data}" accesskey="0">[0]戻る</a><br />
% endif
[9]<a href="/" accesskey="9">トップへ</a><br />
</%block>
<%include file='./_form.mako' args="form=form" />
