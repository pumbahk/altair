<%page args="attentions" />
<h2>注目のイベント</h2>
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
