<%inherit file="../common/_base.mako" />
<%namespace file="../common/tags_mobile.mako" name="m" />
<%block name="title">購入履歴確認</%block>
<%block name="fnavi">
[9]<a href="/" accesskey="9">トップへ</a><br />
</%block>
<a href="${form.altair_orderreview_url.data}">受付番号の頭に<font color="#cc0000">RT</font>がつく方</a><br />
<a href="${form.getti_orderreview_url.data}">受付番号の頭にRTがつかない方</a><br />
