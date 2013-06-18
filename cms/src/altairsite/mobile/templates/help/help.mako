<%inherit file="../common/_base.mako" />
<%namespace file="../common/tags_mobile.mako" name="m" />
<%block name="title">ヘルプ</%block>
<%block name="fnavi">
  [9]<a href="/" accesskey="9">トップへ</a>
</%block>
% if form.helps.data:
    % for help in form.helps.data:
        <a href="#${help.id}">
            ${helper.nl2br(help.title)|n}
        </a><br/><br/>
    % endfor

    <a href="#top">▲上へ</a>

    % for count, help in enumerate(form.helps.data):
        <hr/>
        <a name="${help.id}" id="${help.id}">
            ${helper.nl2br(help.title)|n}<br/><br/>
        </a>
        ${helper.nl2br(help.text)|n}<br/>
        % if (count + 1) % 5 == 0 or len(form.helps.data) == count + 1:
            <hr/>
            <a href="#top">▲上へ</a><br/>
        % endif
    % endfor
% endif
