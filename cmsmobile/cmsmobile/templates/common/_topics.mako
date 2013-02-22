<%page args="topics" />
<h2>トピックス</h2>
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
