<%inherit file="../common/_base.mako" />
<%namespace file="../common/tags_mobile.mako" name="m" />
<%block name="title">公演中止・変更情報</%block>
<%block name="fnavi">
<a href="/" accesskey="0">[0]戻る</a><br />
[9]<a href="/" accesskey="9">トップへ</a><br />
</%block>
% if form.information.data:
    公演：${helper.nl2br(form.information.data.title)|n}<br/>
    詳細：${helper.nl2br(form.information.data.text)|n}<br/><br/>
% else:
    公演中止情報はありません。
% endif
