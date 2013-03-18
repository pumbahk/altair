<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/html">
    <%include file="../common/_header.mako" args="title=u'楽天チケット[公演中止・変更情報]'"/>
<body>

    <a href="/">トップ</a> >> 公演中止・変更情報


    % if form.informations.data:
        % for count, info in enumerate(form.informations.data):

            % if count % 10 == 0:
                <hr/>
                <a href="/">楽天チケットトップへ</a>
            % endif

            <hr/>
            公演：${info.title}<br/>
            詳細：${info.text}<br/>
        % endfor

        % if (len(form.informations.data) + 1 ) % 10 != 0:
            <hr/>
            <a href="/">楽天チケットトップへ</a>
        % endif
    % else:
        公演中止情報はありません。
    % endif
    <%include file="../common/_footer.mako" />
</body>
</html>
