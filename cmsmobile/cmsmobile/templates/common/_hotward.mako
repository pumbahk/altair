<%page args="hotwords" />
<div style="font-size: medium">ホットワード</div>
<span style="font-size: x-small">
% if hotwords:
    % for hotword in hotwords:
        <a href="/hotword?id=${hotword.id}">${hotword.name}</a>
    % endfor
% endif
</span>
