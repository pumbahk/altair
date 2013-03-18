<%page args="topics" />

<div style="background-image:url(../static/bg_bar.gif);background-color:#bf0000;font-size: medium;
                        color: #ffffff" bgcolor="#bf0000" background="../static/bg_bar.gif">トピックス</div>

<div class="line" style="background:#FFFFFF"><img src="../static/clear.gif" alt="" width="1" height="1" /></div>

<span style="font-size: x-small">
% if topics:
    % for topic in topics:
        <a href="/eventdetail?topic_id=${topic.id}">${topic.text}</a>
        <br/>
    % endfor
% endif
</span>
