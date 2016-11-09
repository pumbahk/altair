<%inherit file="base.mako" />
<section class="main error">
<div class="wrap">
<p class="errorText">指定されたURLは正しくありません</p>
</div><!-- /wrap -->
</section><!-- /main -->

<!--SiteCatalyst-->
<%
    sc = {"pagename": "error-notfound"}
%>
<%include file="../common/sc_basic.html" args="sc=sc" />
<!--/SiteCatalyst-->
