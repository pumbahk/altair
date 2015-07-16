<%page args="hotwords, genre, sub_genre, helper" />
<%namespace file="../common/tags_mobile.mako" name="m" />
% if hotwords:
<%m:header>ホットワード</%m:header>
<div>
    % if genre:
        % for hotword in hotwords:
            % if helper.get_events_from_hotword(request, hotword):
                <a href="/hotword?id=${hotword.id}&genre=${genre}&sub_genre=${sub_genre}">${hotword.name}</a>
            % endif
        % endfor
    % else:
        % for count, hotword in enumerate(hotwords):
            % if helper.get_events_from_hotword(request, hotword):
                <a href="/hotword?id=${hotword.id}">${hotword.name}</a>
            % endif
        % endfor
    % endif
</div>
% endif
