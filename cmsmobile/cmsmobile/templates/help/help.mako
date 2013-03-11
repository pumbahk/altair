<!DOCTYPE html>
<html>
<%include file="../common/_header.mako" args="title=u'ヘルプ'"/>
<body>

    <a href="/">トップ</a> >> ヘルプ<p/>

    % if form.helps.data:
        % for help in form.helps.data:
            <a href="#${help.id}">
                <strong>Ｑ．${help.title}</strong><p/>
            </a>
        % endfor

        % for help in form.helps.data:
            <hr/>
            <a name="${help.id}">
                <strong>Ｑ．${help.title}</strong><p/>
            </a>
            Ａ．${help.text}<p/>
        % endfor
    % endif

    <%include file="../common/_footer.mako" />
</body>
</html>