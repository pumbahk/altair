<%include file="../common/_header.mako" args="title=u'ヘルプ'"/>
<body>
<h1>
     ヘルプ</br>
</h1>
    % for help in helps:
        <hr/>
        <strong>Ｑ．${help.title}</strong><p/>
        Ａ．${help.text}<p/>
    % endfor

    <%include file="../common/_footer.mako" />
</body>
</html>
