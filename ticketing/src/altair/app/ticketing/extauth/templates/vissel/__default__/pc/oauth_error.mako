<%inherit file="base.mako" />
<section class="main error">
<div class="wrap">
<p class="errorText">ただいま大変込み合っております。（V003）</p>
アクセス混雑などのため、現在ページが表示しにくい状態となっております。<br/>
お客様にはご迷惑をおかけしますが、今しばらくお待ち頂き、再度アクセスをお願いいたします。<br/>
</div><!-- /wrap -->
</section><!-- /main -->

<!--SiteCatalyst-->
<%
    sc = {"pagename": "error-oauth"}
%>
<%include file="../common/sc_basic.html" args="sc=sc" />
<!--/SiteCatalyst-->
