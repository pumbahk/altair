#### blocks
## info {description,keywords,title  }
## custom {css_prerender,js_prerender}
##
##
##

<%namespace file="./components.mako" name="co"/>

<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="ja" lang="ja">
  <head>
    <meta http-equiv="content-type" content="text/html; charset=utf-8" />
    
    <title><%block name="title"/></title>
    <meta name="description" content="<%block name="description"/>">
    <meta name="keywords" content="<%block name="keywords"/>">
        
    <meta http-equiv="content-style-type" content="text/css" />
    <meta http-equiv="content-script-type" content="text/javascript" />
    <link rel="shortcut icon" href="/static/ticketstar/img//common/favicon.ico" />
    <link rel="stylesheet" href="/static/ticketstar/css/import.css" type="text/css" media="all" />

	<%block name="js_prerender"/>
	<%block name="css_prerender"/>
    <script type="text/javascript" src="/static/ticketstar/js/jquery.js"></script>
  </head>
<body id="music">

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
	
	<!-- InstanceBeginEditable name="cat" --><h1><img src="/static/ticketstar/img/music/title_music.gif" alt="音楽" width="91" height="60" /></h1><!-- InstanceEndEditable -->
	
	<!-- ========== main ========== -->
	<div id="main">
	  <%block name="main"/>
	  <div id="mainLeft">
		<%block name="main_left"/>
	  </div>
	  <div id="mainRight">
		<%block name="main_right"/>
	  </div>
	  <%block name="main_bottom"/>
	</div>
	<!-- ========== /main ========== -->
	
	<hr />
	
	<!-- ========== side ========== -->
	<div id="side">
	  <%block name="side"/>
	</div>
	<!-- ========== /side ========== -->
	
	<hr />
	
	<!-- ========== footer ========== -->
	${co.master_footer()}
	<!-- ========== /footer ========== -->

<!-- /container --></div>
</body>
<!-- InstanceEnd --></html>
