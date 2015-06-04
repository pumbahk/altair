<%page args="attentions, genre, sub_genre, helper" />
<%namespace file="../common/tags_mobile.mako" name="m" />
<% attentions = [(event, attention) for event, attention in ((helper.get_event_from_linked_page_id(request, attention.linked_page_id), attention) for attention in attentions)] %>

% if attentions:
<%m:header>注目のイベント</%m:header>
<div>
    % for event, attention in attentions:
        <%
            link = None
            if attention.mobile_link:
                link = attention.mobile_link
            elif event:
                link = request.mobile_route_path("eventdetail", _query=dict(event_id=event.id))
        %>

        % if link:
            <a href=${link}>${attention.text}</a><br />
        % else:
            % if helper.get_eventsqs_from_mobile_tag_id(request, attention.mobile_tag_id).all():
                <a href="${request.mobile_route_path('mobile_tag_search', mobile_tag_id=attention.mobile_tag_id, genre=genre, sub_genre=sub_genre if sub_genre else "0", page=1)}">${attention.text}</a><br/>
            % else:
                ${attention.text}<br/>
            % endif
        % endif
    % endfor
</div>
% endif
