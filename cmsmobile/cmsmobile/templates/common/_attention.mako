<%page args="attentions" />
<div style="background-image:url(../static/bg_bar.gif);background-color:#bf0000;
                        color: #ffffff" bgcolor="#bf0000" background="../static/bg_bar.gif">注目のイベント</div>

<div class="line" style="background:#FFFFFF"><img src="../static/clear.gif" alt="" width="1" height="1" /></div>

% if attentions:
    % for count, attention in enumerate(attentions):
        <a href="/eventdetail?attention_id=${attention.id}">${attention.text}</a>
        % if count < len(attentions) - 1:
        /
        % endif
    % endfor
% endif
