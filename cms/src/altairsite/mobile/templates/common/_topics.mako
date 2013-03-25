<%page args="topics, genre, sub_genre, helper" />

<div style="background-image:url(../static/bg_bar.gif);background-color:#bf0000" bgcolor="#bf0000"><font color="#ffffff" size="3"><font color="#ffbf00">■</font>トピックス</font></div>

<div class="line" style="background:#FFFFFF"><img src="../static/clear.gif" alt="" width="1" height="1" /></div>

% if topics:
    % for topic in topics:
        % if genre:
            % if helper.get_event_from_topic(request, topic):
                <a href="/eventdetail?event_id=${helper.get_event_from_topic(request, topic).id}&genre=${genre}&sub_genre=${sub_genre}">${topic.text}</a>
            % else:
                ${topic.text}
            % endif
        % else:
            % if helper.get_event_from_topic(request, topic):
                <a href="/eventdetail?event_id=${helper.get_event_from_topic(request, topic).id}">${topic.text}</a>
            % else:
                ${topic.text}
            % endif
        % endif
        <br/>
    % endfor
% endif
