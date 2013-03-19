<%page args="hotwords, genre, sub_genre" />
<div style="background-image:url(../static/bg_bar.gif);background-color:#bf0000" bgcolor="#bf0000"><font color="#ffffff" size="3"><font color="#ffbf00">■</font>ホットワード</font></div>

<div class="line" style="background:#FFFFFF"><img src="../static/clear.gif" alt="" width="1" height="1" /></div>

% if hotwords:
    % if genre:
        % for hotword in hotwords:
            <a href="/hotword?id=${hotword.id}&genre=${genre}&sub_genre=${sub_genre}">${hotword.name}</a>
        % endfor
    % else:
        % for hotword in hotwords:
            <a href="/hotword?id=${hotword.id}">${hotword.name}</a>
        % endfor
    % endif
% endif
