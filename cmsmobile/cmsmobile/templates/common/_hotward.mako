<%page args="hotwords" />
<h2>ホットワード</h2>
% if hotwords:
    % for hotword in hotwords:
        <a href="/hotword?id=${hotword.id}">${hotword.name}</a>
    % endfor
% endif
