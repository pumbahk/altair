<%page args="topics" />
<h1>トピックス</h1>
% if topics:
    <ul>
        % for topic in topics:
            <li>
                % if topic.mobile_link:
                    <a href="${topic.mobile_link}">${topic.text}</a>
                % else:
                    ${topic.text}
                % endif
            </li>
        % endfor
    </ul>
% endif
