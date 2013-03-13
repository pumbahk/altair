<%page args="topics" />
<h2>トピックス</h2>
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
