<%page args="topics, genre, sub_genre, helper" />
<%namespace file="../common/tags_mobile.mako" name="m" />

<% topics = [(event, topic) for event, topic in ((helper.get_event_from_linked_page_id(request, topic.linked_page_id), topic) for topic in topics)] %>

% if topics:
<%m:header>トピックス</%m:header>
<div>
    % for event, topic in topics:
        % if event:
            <a href="/eventdetail?event_id=${event.id}">${topic.text}</a><br />
        % else:
            % if helper.get_eventsqs_from_mobile_tag_id(request, topic.mobile_tag_id).all():
                <a href="${request.mobile_route_path('mobile_tag_search', mobile_tag_id=topic.mobile_tag_id, genre=genre, sub_genre=sub_genre if sub_genre else "0", page=1)}">${topic.text}</a><br/>
            % else:
                ${topic.text}<br/>
            % endif
        % endif
    % endfor
</div>
% endif
