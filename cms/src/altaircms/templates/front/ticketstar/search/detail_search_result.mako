<%doc>
${queries}
detail search result
</%doc>

<%namespace file="../components.mako" name="co"/>

<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="ja" lang="ja"><!-- InstanceBegin template="/Templates/template.dwt" codeOutsideHTMLIsLocked="false" -->
<head>
<meta http-equiv="content-type" content="text/html; charset=utf-8" />
<!-- InstanceBeginEditable name="doctitle" -->
<title>チケット販売・イベントの予約 [音楽 / コンサート / 舞台 / スポーツ] - 楽天チケット</title>
<!-- InstanceEndEditable -->
<meta name="description" content="チケットの販売、イベントの予約は楽天チケットで！楽天チケットは演劇、バレエ、ミュージカルなどの舞台、クラシック、オペラ、ロックなどのコンサート、野球、サッカー、格闘技などのスポーツ、その他イベントなどのチケットのオンラインショッピングサイトです。" />
<meta name="keywords" content="チケット,演劇,クラシック,オペラ,コンサート,バレエ,ミュージカル,野球,サッカー,格闘技" />
<meta http-equiv="content-style-type" content="text/css" />
<meta http-equiv="content-script-type" content="text/javascript" />
<link rel="shortcut icon" href="/static/ticketstar/img/common/favicon.ico" />
<link rel="stylesheet" href="/static/ticketstar/css/import.css" type="text/css" media="all" />
<script type="text/javascript" src="/static/ticketstar/js/jquery.js"></script>
<!-- InstanceParam name="id" type="text" value="search" -->
</head>
<body id="search">

<p id="naviSkip"><a href="#main" tabindex="1" title="本文へジャンプ"><img src="/static/ticketstar/img/common/skip.gif" alt="本文へジャンプ" width="1" height="1" /></a></p>

<div id="container">

	<!-- ========== header ========== -->
	<div id="grpheader">
  	  ${co.master_header()}
    </div>
    ${co.global_navigation(top_inner_categories, categories)}
    ${co.header_search()}
	<!-- ========== /header ========== -->
	
	<hr />
	
	<!-- InstanceBeginEditable name="cat" --><h1><img src="/static/ticketstar/img/search/title_search.gif" alt="検索結果" width="118" height="60" /></h1>
<!-- InstanceEndEditable -->
	
	<!-- ========== main ========== -->
	<div id="main">
		<!-- InstanceBeginEditable name="main" -->
		<%block name="main"/>
		<!-- InstanceEndEditable -->
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

