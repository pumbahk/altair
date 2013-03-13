<%page args="attentions" />
<div style="background-image:url(../static/bg_bar.gif);background-color:#bf0000;font-size: medium;
                        color: #ffffff" bgcolor="#bf0000" background="../static/bg_bar.gif">注目のイベント</div>

<span style="font-size: x-small">
% if attentions:
    % for attention in attentions:
        % if attention.mobile_link:
            <a href="${attention.mobile_link}">${attention.text}</a>
        % else:
            ${attention.text}
        % endif
        /
    % endfor
% endif
</span>