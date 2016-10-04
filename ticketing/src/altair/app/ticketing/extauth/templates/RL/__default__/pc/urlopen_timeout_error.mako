<%inherit file="base.mako" />
<div class="errorBox">
<p class="errorText">ただいま大変込み合っております。（E006）</p>
アクセス混雑などのため、現在ページが表示しにくい状態となっております。<br/>
お客様にはご迷惑をおかけしますが、今しばらくお待ち頂き、再度アクセスをお願いいたします。<br/>
</div>

<!--SiteCatalyst-->
<%
    sc = {"pagename": "error-fatal"}
%>
<%include file="../common/sc_basic.html" args="sc=sc" />
<!--/SiteCatalyst-->
