<%page args="hotwords" />
<div style="background-image:url(../static/bg_bar.gif);background-color:#bf0000;font-size: medium;
                        color: #ffffff" bgcolor="#bf0000" background="../static/bg_bar.gif">ホットワード</div>

<div class="line" style="background:#FFFFFF"><img src="../static/clear.gif" alt="" width="1" height="1" /></div>

<span style="font-size: x-small">
% if hotwords:
    % for hotword in hotwords:
        <a href="/hotword?id=${hotword.id}">${hotword.name}</a>
    % endfor
% endif
</span>
