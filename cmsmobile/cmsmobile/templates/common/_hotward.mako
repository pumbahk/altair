<%page args="hotwords" />
<h2>ホットワード</h2>
% if hotwords:
    % for hotword in hotwords:
        ${hotword.name}
    % endfor
% endif
