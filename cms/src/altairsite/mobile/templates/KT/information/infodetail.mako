<%inherit file="../common/_base.mako" />
<%namespace file="../common/tags_mobile.mako" name="m" />
<%block name="title">公演中止・変更情報</%block>
<%block name="fnavi">
<a href="/" accesskey="0">[0]戻る</a><br />
[9]<a href="/" accesskey="9">トップへ</a><br />
</%block>
% if form.informations.data:
    % for count, info in enumerate(form.informations.data):
        公演：${helper.nl2br(info.title)|n}<br/>
        詳細：${helper.nl2br(info.text)|n}<br/><br/>
        <a href="#top">▲上へ</a>
        % if count < len(form.informations.data) - 1:
            <hr/>
        % endif
    % endfor

% else:
    公演中止情報はありません。
% endif
