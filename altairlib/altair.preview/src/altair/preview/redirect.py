# -*- coding:utf-8 -*-
from .interfaces import IPreviewRedirect
from pyramid.response import Response
from zope.interface import implementer
from altair.now import get_now

class Failure(unicode):
    """permission"""
    def __nonzero__(self):
        return False

@implementer(IPreviewRedirect)
class PreviewRedirectDefault(object):
    CSS_TEMPLATE = u"""
<style type="text/css">
.preview-box{
position: fixed;
top: 0px;
left: 100px;
padding: 0px 20px;
background-color: green;
font-size: 14pt;
color: white;
z-index: 1000;
}
.logout-box{
display: inline;
margin-left: 150px;
}
.preview-box a:link,.preview-box a:visited{
color: white;
}
</style>
"""

    def on_success(self, request, response, permission):
        embed = u"""
</head>
{css}
<div class="preview-box">
preview中 現在時刻: {now}
<div class="logout-box">
 <a href="{logout_url}">logout</a>
</div>
</div>
""".format(css=self.CSS_TEMPLATE, now=get_now(request), logout_url=request.route_path("__altair.preview.invalidate"))
        response.body = response.text.replace(u"</head>", embed).encode("utf-8")
        return response

    def on_failure(self, request, response, permission):
        body = u"""
<html>
<body>
  <div class="logout-box">
     <a href="{logout_url}">logout</a>
  </div>
<p>{message}</p>
  <div class="logout-box">
     <a href="{logout_url}">logout</a>
  </div>
</body>
</html>
""".format(message=permission, logout_url=request.route_path("__altair.preview.invalidate"))
        return Response(body)
    
