<%inherit file="../common/_base.mako" />
<%namespace file="../common/tags_mobile.mako" name="m" />
<%block name="title">ホットワード</%block>
<%block name="fnavi">
  [9]<a href="/" accesskey="9">トップへ</a>
</%block>
<%include file='../common/_search_result.mako' args="form=form, events=events" />
