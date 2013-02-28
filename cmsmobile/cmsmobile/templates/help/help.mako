<%include file="../common/_header.mako" args="title=u'ヘルプ'"/>
<body>

    <a href="/">トップ</a> >> ヘルプ<p/>

    % if helps:
        % for help in helps:
            <a href="#${help.id}">
                <strong>Ｑ．${help.title}</strong><p/>
            </a>
        % endfor

        % for help in helps:
            <hr/>
            <a name="${help.id}">
                <strong>Ｑ．${help.title}</strong><p/>
            </a>
            Ａ．${help.text}<p/>
        % endfor
    % endif:

    <%include file="../common/_footer.mako" />
</body>
</html>
