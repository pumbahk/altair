<%page args="attentions, genre, sub_genre, helper" />
<%namespace file="../common/tags_mobile.mako" name="m" />
% if attentions:
<%m:header>注目のイベント</%m:header>
<div>
  <% first = True %>
    % for attention in attentions:
        % if attention.mobile_tag_id:
            <a href="${request.mobile_route_path('mobile_tag_search', mobile_tag_id=attention.mobile_tag_id, genre=genre, sub_genre=sub_genre if sub_genre else "0", page=1)}">${attention.text}</a>
        % else:
            ${attention.text}<br/>
        % endif
    % endfor
</div>
% endif
