<%page args="attentions" />
<h1>注目のイベント</h1>
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
