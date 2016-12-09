<%inherit file="base.mako" />
<section class="main error">
<div class="wrap">
<p class="errorText">ただいま大変込み合っております。（V000）</p>
</div><!-- /wrap -->
</section><!-- /main -->

<!--SiteCatalyst-->
<%
    sc = {"pagename": "error-fatal"}
%>
<%include file="../common/sc_basic.html" args="sc=sc" />
<!--/SiteCatalyst-->
