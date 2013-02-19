<%page args="topics" />
<h1>トピックス</h1>
% for topic in topics:
    % if topic.mobile_link:
        <a href="${topic.mobile_link}">${topic.text}</a>
    % else:
        ${topic.text}
    % endif
    /
% endfor
