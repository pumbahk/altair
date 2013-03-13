<%page args="topics" />
<div style="font-size: medium">トピックス</div>
<span style="font-size: x-small">
% if topics:
    % for topic in topics:
        % if topic.mobile_link:
            <a href="${topic.mobile_link}">${topic.text}</a>
        % else:
            ${topic.text}
        % endif
        <br/>
    % endfor
% endif
</span>
