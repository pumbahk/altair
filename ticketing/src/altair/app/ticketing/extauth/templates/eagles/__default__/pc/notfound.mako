<%inherit file="base.mako" />
<div class="errorBox">
<p class="errorText">指定されたURLは正しくありません</p>
</div>

<!--SiteCatalyst-->
<%
    sc = {"pagename": "error-notfound"}
%>
<%include file="../common/sc_basic.html" args="sc=sc" />
<!--/SiteCatalyst-->
