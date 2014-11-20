<%inherit file="../common/_base.mako" />
<%namespace file="../common/tags_mobile.mako" name="m" />
<%block name="title">公演中止情報</%block>
<%block name="fnavi">
[9]<a href="/" accesskey="9">トップへ</a><br />
</%block>
% if form.informations.data:
    % for count, info in enumerate(form.informations.data):
        <a href="${request.mobile_route_path('infodetail', _query=dict(information_id=info.id))}">
        公演：${helper.nl2br(info.title)|n}<br/>
        </a>
        <hr/>
    % endfor
% else:
    公演中止・変更情報はありません。
% endif
