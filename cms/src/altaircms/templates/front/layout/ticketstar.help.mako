<%inherit file="altaircms:templates/front/ticketstar/help.mako"/>
##<%namespace file="./components/ticketstar/help/header.mako" name="header_co"/>
##<%namespace file="./components/ticketstar/help/userbox.mako" name="userbox_co"/>

<%def name="widgets(name)">
  % for w in display_blocks[name]:
      ${w|n}
  % endfor
</%def>

<%block name="main">
   ${widgets("main")}
</%block>

<%block name="side">
		<!-- InstanceBeginEditable name="side" -->
		<ul id="sideNav">
			<li id="sideNavFirst"><a href="#help1">会員登録・ログイン</a></li>
			<li><a href="#help2">チケット予約・購入</a></li>
			<li><a href="#help3">支払方法・引取方法</a></li>
			<li><a href="#help4">本人認証サービス(3Dセキュアサービス)について</a></li>
			<li><a href="#help5">セブン－イレブン引取</a></li>
		</ul>
		<!-- InstanceEndEditable -->
		<ul id="sideBtn">
			<li><a href="#"><img src="/static/ticketstar/img/mypage/btn_use.gif" alt="楽天チケットの使い方" width="202" height="28" /></a></li>
			<li><a href="#"><img src="/static/ticketstar/img/mypage/btn_favorite.gif" alt="お気に入りアーティストを登録" width="202" height="28" /></a></li>
			<li><a href="#"><img src="/static/ticketstar/img/mypage/btn_magazine.gif" alt="メルマガの購読" width="202" height="28" /></a></li>
		</ul>
</%block>
