<%page args="hotwords, genre, sub_genre, helper" />
<div style="background-image:url(../static/bg_bar.gif);background-color:#bf0000" bgcolor="#bf0000"><font color="#ffffff" size="3"><font color="#ffbf00">■</font>ホットワード</font></div>

<div class="line" style="background:#FFFFFF"><img src="../static/clear.gif" alt="" width="1" height="1" /></div>

% if hotwords:
    % if genre:
        % for hotword in hotwords:
            % if helper.get_events_from_hotword(request, hotword):
                <a href="/hotword?id=${hotword.id}&genre=${genre}&sub_genre=${sub_genre}">${hotword.name}</a>
            % else:
                ${hotword.name}
            % endif
        % endfor
    % else:
        % for count, hotword in enumerate(hotwords):
            % if helper.get_events_from_hotword(request, hotword):
                <a href="/hotword?id=${hotword.id}">${hotword.name}</a>
            % else:
                ${hotword.name}
            % endif
            % if count < len(hotwords) - 1:
                 / 
            % endif
        % endfor
    % endif
% endif
