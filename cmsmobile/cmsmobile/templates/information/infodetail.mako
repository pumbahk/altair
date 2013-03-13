<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/html">
    <%include file="../common/_header.mako" args="title=u'楽天チケット[公演中止・変更情報]'"/>
<body>

<div style="font-size: x-small">
    <a href="/">トップ</a> >> 公演中止・変更情報
</div>

    % if form.informations.data:
        % for count, info in enumerate(form.informations.data):

            % if count % 10 == 0:
                <hr/>
                <a href="/"><span style="font-size: x-small">楽天チケットトップへ</span></a>
            % endif

            <hr/>
            <div style="font-size: x-small">公演：${info.title}</div>
            <span style="font-size: x-small">詳細：${info.text}</span>
        % endfor

        % if (len(form.informations.data) + 1 ) % 10 != 0:
            <hr/>
            <a href="/"><span style="font-size: x-small">楽天チケットトップへ</span></a>
        % endif
    % else:
        <span style="font-size: x-small">公演中止情報はありません。</span>
    % endif
    <%include file="../common/_footer.mako" />
</body>
</html>
