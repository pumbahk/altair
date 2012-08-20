<%namespace file="./components/ticketstar/top/side.mako" name="side_co"/>

<%def name="widgets(name)">
  % for w in display_blocks[name]:
      ${w|n}
  % endfor
</%def>


#### blocks
## info {description,keywords,title  }
## custom {css_prerender,js_prerender}
## main{main,main_left,main_right,main_bottom }
## side{side_top,side_bottom}
##

<%namespace file="../ticketstar/components.mako" name="co"/>
<%namespace file="altaircms:templates/front/ticketstar/gadgets.mako" name="gadgets"/>

<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="ja" lang="ja">
<head>
<meta http-equiv="content-type" content="text/html; charset=utf-8" />

    <title>${page.title}</title>
    <meta name="description" content="${page.description}">
    <meta name="keywords" content="${page.keywords}">

<meta http-equiv="content-style-type" content="text/css" />
<meta http-equiv="content-script-type" content="text/javascript" />
<link rel="shortcut icon" href="/static/ticketstar/img/common/favicon.ico" />
<link rel="stylesheet" href="/static/ticketstar/css/import.css" type="text/css" media="all" />
<script type="text/javascript" src="/static/ticketstar/js/jquery.js"></script>
</head>
<body id="index">

<p id="naviSkip"><a href="#main" tabindex="1" title="本文へジャンプ"><img src="/static/ticketstar/img/common/skip.gif" alt="本文へジャンプ" width="1" height="1" /></a></p>

<div id="container">

	<!-- ========== header ========== -->
	<div id="grpheader">
  	  ${co.master_header()}
    </div>
    ${co.global_navigation()}
    ${co.header_search()}
	<!-- ========== /header ========== -->
	
	<hr />

	<!-- ========== main ========== -->
	<div id="main">
<%block name="main">
   ${widgets("main")}
</%block>
	  <div id="mainLeft">
<%block name="main_left">
   ${widgets("main_left")}
</%block>
	  </div>
	  <div id="mainRight">
<%block name="main_right">
   ${widgets("main_right")}
</%block>
	  </div>
<%block name="main_bottom">
   ${widgets("main_bottom")}
</%block>
	</div>
	<!-- ========== /main ========== -->
	
	<hr />
	
	<!-- ========== side ========== -->
	<div id="side">
<%block name="side_top">
   ${widgets("side_top")}
</%block>
       ${gadgets.top_side_searchform()}
<%block name="side_bottom">
   ${widgets("side_bottom")}
</%block>

	</div>
	<!-- ========== /side ========== -->
	
	<hr />
	
	<!-- ========== footer ========== -->
	${co.master_footer()}
	<!-- ========== /footer ========== -->

<!-- /container --></div>

</body>
</html>
