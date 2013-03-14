<%page args="attentions" />
<div style="background-image:url(../static/bg_bar.gif);background-color:#bf0000;font-size: medium;
                        color: #ffffff" bgcolor="#bf0000" background="../static/bg_bar.gif">注目のイベント</div>

<span style="font-size: x-small">
% if attentions:
    % for count, attention in enumerate(attentions):
        <a href="/eventdetail?attention_id=${attention.id}">${attention.text}</a>
        % if count < len(attentions) - 1:
        /
        % endif
    % endfor
% endif
</span>