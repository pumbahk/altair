<%def name="widgets(name)">
  % for w in display_blocks[name]:
      ${w|n}
  % endfor
</%def>

#### block
## main{main,main_left,main_right,main_bottom }
## side

<%namespace file="altaircms:templates/front/ticketstar/gadgets.mako" name="gadgets"/>
<%namespace file="../ticketstar/components.mako" name="co"/>

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
    <link rel="shortcut icon" href="/static/ticketstar/img//common/favicon.ico" />
    <link rel="stylesheet" href="/static/ticketstar/css/import.css" type="text/css" media="all" />

	<%block name="js_prerender"/>
	<%block name="css_prerender"/>
    <script type="text/javascript" src="/static/ticketstar/js/jquery.js"></script>
  </head>
<body id="sports">

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
	
	<!-- InstanceBeginEditable name="cat" --><h1><img id="titleImage" src="/static/ticketstar/img/sports/title_sports.gif" alt="スポーツ"/></h1><!-- InstanceEndEditable -->
	
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
</%block>
	</div>
	<!-- ========== /main ========== -->
	
	<hr />
	
	<!-- ========== side ========== -->
	<div id="side">
<%block name="side">
		<!-- InstanceBeginEditable name="side" -->
		${widgets("side")}
  	    ${gadgets.sidebar_genre_listing(sub_categories)}

		<dl id="sideRefineSearch">
            ${gadgets.sidebar_area_listing(areas)}
            ${gadgets.sidebar_deal_cond_listing()}
			${gadgets.sidebar_deal_open_listing()}
			${gadgets.sidebar_event_open_listing()}
		</dl>

##		${gadgets.sidebar_maintenance()}
		<!-- InstanceEndEditable -->
##		${gadgets.sidebar_sideBtn()}
</%block>
	</div>
	<!-- ========== /side ========== -->
	
	<hr />
	
	<!-- ========== footer ========== -->
	${co.master_footer()}
	<!-- ========== /footer ========== -->

<!-- /container --></div>
</body>
<!-- InstanceEnd --></html>


