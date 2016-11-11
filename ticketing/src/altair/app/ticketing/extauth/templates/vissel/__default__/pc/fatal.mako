<%inherit file="base.mako" />
<section class="main error">
<div class="wrap">
<p class="errorText">致命的なエラーが発生しました</p>
</div><!-- /wrap -->
</section><!-- /main -->

<!--SiteCatalyst-->
<%
    sc = {"pagename": "error-fatal"}
%>
<%include file="../common/sc_basic.html" args="sc=sc" />
<!--/SiteCatalyst-->
