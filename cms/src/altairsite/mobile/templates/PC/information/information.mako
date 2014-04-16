<%inherit file="../common/_base.mako" />
<%namespace file="../common/tags_mobile.mako" name="m" />
<%block name="title">公演中止情報</%block>
<%block name="fnavi">
[9]<a href="/" accesskey="9">トップへ</a><br />
</%block>
% if form.informations.data:
    % for count, info in enumerate(form.informations.data[0:5]):
        % if count > 0:
            <hr/>
        % endif
        公演：${helper.nl2br(info.title)|n}<br/>
        詳細：${helper.nl2br(info.text)|n}<br/>
        <br/>
        <a href="#top">▲上へ</a>
    % endfor

    % if len(form.informations.data) > 5:
        <hr/>
        <a href="/infodetail">すべてを見る</a>
    % endif
% else:
    公演中止・変更情報はありません。
% endif
