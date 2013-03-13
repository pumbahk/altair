<%page args="attentions" />
<div style="font-size: medium">注目のイベント</div>
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