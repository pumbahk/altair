<%page args="topics, genre, sub_genre, helper" />
<%namespace file="../common/tags_mobile.mako" name="m" />
<% topics = [(event, topic) for event, topic in ((helper.get_event_from_topic(request, topic), topic) for topic in topics) if event] %>
% if topics:
<%m:header>トピックス</%m:header>
<div>
    % for event, topic in topics:
        % if genre:
            <a href="/eventdetail?event_id=${event.id}&genre=${genre}&sub_genre=${sub_genre}">${topic.text}</a><br />
        % else:
            <a href="/eventdetail?event_id=${event.id}">${topic.text}</a><br />
        % endif
    % endfor
</div>
% endif
