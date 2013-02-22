<%include file="../common/_header.mako" args="title=u'公演中止情報'"/>
<body>

    <a href="/">トップ</a> >> 公演中止・変更情報<p/>

    % for info in informations:
        <hr/>
        公演：${info.title}<br/>
        詳細：${info.text}
    % endfor
    <%include file="../common/_footer.mako" />
</body>
</html>
