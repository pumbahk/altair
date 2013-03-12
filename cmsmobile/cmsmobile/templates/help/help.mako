<!DOCTYPE html>
<html>
<%include file="../common/_header.mako" args="title=u'楽天チケット[ヘルプ]'"/>
<body>

    <a href="/">トップ</a> >> ヘルプ<p/>

    % if form.helps.data:
        % for help in form.helps.data:
            <a href="#${help.id}">
                <strong>Ｑ．${help.title}</strong><br/>
            </a>
        % endfor

        <p/>
        <a href="/">楽天チケットトップへ</a>

        % for count, help in enumerate(form.helps.data):
            % if count % 5 == 0 and count != 0:
                <hr/>
                <a href="/">楽天チケットトップへ</a>
            % endif
            <hr/>
            <a name="${help.id}">
                <strong>Ｑ．${help.title}</strong><p/>
            </a>
            Ａ．${help.text}<p/>
            ${count}
        % endfor

        % if (len(form.helps.data) + 1 ) % 5 != 0:
            <hr/>
            <a href="/">楽天チケットトップへ</a>
        % endif
    % endif

    <%include file="../common/_footer.mako" />
</body>
</html>