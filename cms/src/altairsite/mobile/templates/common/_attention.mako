<%page args="attentions, genre, sub_genre, helper" />
<%namespace file="../common/tags_mobile.mako" name="m" />
% if attentions:
<%m:header>注目のイベント</%m:header>
<div>
  <% first = True %>
    % for attention in attentions:
        % if genre:
            % if helper.get_event_from_topcontent(request, attention):
                <a href="/eventdetail?event_id=${helper.get_event_from_topcontent(request, attention).id}&genre=${genre}&sub_genre=${sub_genre}">${attention.text}</a><br />
            % else:
                ${attention.text}<br/>
            % endif
        % else:
            % if helper.get_event_from_topcontent(request, attention):
                <a href="/eventdetail?event_id=${helper.get_event_from_topcontent(request, attention).id}">${attention.text}</a><br />
            % else:
                ${attention.text}<br/>
            % endif
        % endif
    % endfor
</div>
% endif
