<%page args="topics, genre, sub_genre" />

<div style="background-image:url(../static/bg_bar.gif);background-color:#bf0000;
                        color: #ffffff" bgcolor="#bf0000" background="../static/bg_bar.gif">トピックス</div>

<div class="line" style="background:#FFFFFF"><img src="../static/clear.gif" alt="" width="1" height="1" /></div>

% if topics:
    % for topic in topics:
        % if genre:
            <a href="/eventdetail?topic_id=${topic.id}&genre=${genre}&sub_genre=${sub_genre}">${topic.text}</a>
        % else:
            <a href="/eventdetail?topic_id=${topic.id}">${topic.text}</a>
        % endif
        <br/>
    % endfor
% endif
