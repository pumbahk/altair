<%page args="attentions, genre, sub_genre, helper" />

<div style="background-image:url(../static/bg_bar.gif);background-color:#bf0000" bgcolor="#bf0000"><font color="#ffffff" size="3"><font color="#ffbf00">■</font>注目のイベント</font></div>

<div class="line" style="background:#FFFFFF"><img src="../static/clear.gif" alt="" width="1" height="1" /></div>

% if attentions:
    % for count, attention in enumerate(attentions):
        % if genre:
            % if helper.get_event_from_topcontent(request, attention):
                <a href="/eventdetail?event_id=${helper.get_event_from_topcontent(request, attention).id}&genre=${genre}&sub_genre=${sub_genre}">${attention.text}</a>
            % else:
                ${attention.text}
            % endif
        % else:
            % if helper.get_event_from_topcontent(request, attention):
                <a href="/eventdetail?event_id=${helper.get_event_from_topcontent(request, attention).id}">${attention.text}</a>
            % else:
                ${attention.text}
            % endif
        % endif
        % if count < len(attentions) - 1:
        /
        % endif
    % endfor
% endif
