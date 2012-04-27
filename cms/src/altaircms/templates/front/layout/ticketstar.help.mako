<%inherit file="altaircms:templates/front/ticketstar/help.mako"/>
##<%namespace file="./components/ticketstar/help/header.mako" name="header_co"/>
##<%namespace file="./components/ticketstar/help/userbox.mako" name="userbox_co"/>



<%block name="main">
		<!-- InstanceBeginEditable name="main" -->
		<script type="text/javascript">
		$(function() {
			$('.helpList dd').hide();
			$('.helpList dt').click(function() {
				$(this).nextUntil('.helpList dt').toggle();
			});
			$('.helpClose').click(function() {
				$(this).parent().hide();
			});
		});
		</script>
		<h2 id="help1"><img src="/static/ticketstar/img/help/title_regist.gif" alt="会員登録・ログイン" width="742" height="43" /></h2>
		<dl class="helpList">
			<dt>会員IDを忘れてしまいました。</dt>
			<dd><img src="/static/ticketstar/img/help/icon_a.gif" alt="" width="20" height="20" class="helpAnswer" /><a href="#">楽天会員情報</a>の管理よりお手続きください。<img src="/static/ticketstar/img/common/btn_delete.gif" alt="閉じる" width="16" height="16" class="helpClose" /></dd>
			<dt>パスワードを忘れてしまいました。</dt>
			<dd><img src="/static/ticketstar/img/help/icon_a.gif" alt="" width="20" height="20" class="helpAnswer" />回答が入ります。<img src="/static/ticketstar/img/common/btn_delete.gif" alt="閉じる" width="16" height="16" class="helpClose" /></dd>
			<dt>登録している住所やメールアドレスの変更はできますか？</dt>
			<dd><img src="/static/ticketstar/img/help/icon_a.gif" alt="" width="20" height="20" class="helpAnswer" />回答が入ります。<img src="/static/ticketstar/img/common/btn_delete.gif" alt="閉じる" width="16" height="16" class="helpClose" /></dd>
		</dl>
		<h2 id="help2"><img src="/static/ticketstar/img/help/title_buy.gif" alt="チケット予約・購入" width="742" height="43" /></h2>
		<dl class="helpList">
			<dt>座席を指定しての申し込みはできますか？</dt>
			<dd><img src="/static/ticketstar/img/help/icon_a.gif" alt="" width="20" height="20" class="helpAnswer" />回答が入ります。<img src="/static/ticketstar/img/common/btn_delete.gif" alt="閉じる" width="16" height="16" class="helpClose" /></dd>
			<dt>座席はならびで取ることはできますか？</dt>
			<dd><img src="/static/ticketstar/img/help/icon_a.gif" alt="" width="20" height="20" class="helpAnswer" />回答が入ります。<img src="/static/ticketstar/img/common/btn_delete.gif" alt="閉じる" width="16" height="16" class="helpClose" /></dd>
			<dt>一般予約の申し込み方法を教えてください。</dt>
			<dd><img src="/static/ticketstar/img/help/icon_a.gif" alt="" width="20" height="20" class="helpAnswer" />回答が入ります。<img src="/static/ticketstar/img/common/btn_delete.gif" alt="閉じる" width="16" height="16" class="helpClose" /></dd>
			<dt>申し込みしたチケットの座席番号確認はできますか？</dt>
			<dd><img src="/static/ticketstar/img/help/icon_a.gif" alt="" width="20" height="20" class="helpAnswer" />回答が入ります。<img src="/static/ticketstar/img/common/btn_delete.gif" alt="閉じる" width="16" height="16" class="helpClose" /></dd>
			<dt>一度申込みしたチケットの取り消しはできますか？</dt>
			<dd><img src="/static/ticketstar/img/help/icon_a.gif" alt="" width="20" height="20" class="helpAnswer" />回答が入ります。回答が入ります。回答が入ります。回答が入ります。回答が入ります。回答が入ります。回答が入ります。回答が入ります。回答が入ります。回答が入ります。回答が入ります。回答が入ります。回答が入ります。<img src="/static/ticketstar/img/common/btn_delete.gif" alt="閉じる" width="16" height="16" class="helpClose" /></dd>
			<dt>ＰＣから、チケットの申込みができませんでした。</dt>
			<dd><img src="/static/ticketstar/img/help/icon_a.gif" alt="" width="20" height="20" class="helpAnswer" />画面上にエラーメッセージが表示されている場合はその内容を控えていただき、弊社お問合せ先から、お使いの機種・OS（Ｗｉndows XP・ＭａcOS 9等）、お使いのブラウザ及びそのバージョン等エラーの状況をお問い合せください。<img src="/static/ticketstar/img/common/btn_delete.gif" alt="閉じる" width="16" height="16" class="helpClose" /></dd>
			<dt>チケットの予約・購入履歴を確認したい。</dt>
			<dd><img src="/static/ticketstar/img/help/icon_a.gif" alt="" width="20" height="20" class="helpAnswer" />回答が入ります。<img src="/static/ticketstar/img/common/btn_delete.gif" alt="閉じる" width="16" height="16" class="helpClose" /></dd>
		</dl>
		<h2 id="help3"><img src="/static/ticketstar/img/help/title_payment.gif" alt="支払方法・引取方法" width="742" height="43" /></h2>
		<dl class="helpList">
			<dt>会員IDを忘れてしまいました。</dt>
			<dd><img src="/static/ticketstar/img/help/icon_a.gif" alt="" width="20" height="20" class="helpAnswer" />回答が入ります。<img src="/static/ticketstar/img/common/btn_delete.gif" alt="閉じる" width="16" height="16" class="helpClose" /></dd>
			<dt>パスワードを忘れてしまいました。</dt>
			<dd><img src="/static/ticketstar/img/help/icon_a.gif" alt="" width="20" height="20" class="helpAnswer" />回答が入ります。<img src="/static/ticketstar/img/common/btn_delete.gif" alt="閉じる" width="16" height="16" class="helpClose" /></dd>
			<dt>登録している住所やメールアドレスの変更はできますか？</dt>
			<dd><img src="/static/ticketstar/img/help/icon_a.gif" alt="" width="20" height="20" class="helpAnswer" />回答が入ります。<img src="/static/ticketstar/img/common/btn_delete.gif" alt="閉じる" width="16" height="16" class="helpClose" /></dd>
		</dl>
		<h2 id="help4"><img src="/static/ticketstar/img/help/title_secure.gif" alt="本人認証サービス(3Dセキュアサービス)について" width="742" height="43" /></h2>
		<dl class="helpList">
			<dt>会員IDを忘れてしまいました。</dt>
			<dd><img src="/static/ticketstar/img/help/icon_a.gif" alt="" width="20" height="20" class="helpAnswer" />回答が入ります。<img src="/static/ticketstar/img/common/btn_delete.gif" alt="閉じる" width="16" height="16" class="helpClose" /></dd>
			<dt>パスワードを忘れてしまいました。</dt>
			<dd><img src="/static/ticketstar/img/help/icon_a.gif" alt="" width="20" height="20" class="helpAnswer" />回答が入ります。<img src="/static/ticketstar/img/common/btn_delete.gif" alt="閉じる" width="16" height="16" class="helpClose" /></dd>
			<dt>登録している住所やメールアドレスの変更はできますか？</dt>
			<dd><img src="/static/ticketstar/img/help/icon_a.gif" alt="" width="20" height="20" class="helpAnswer" />回答が入ります。<img src="/static/ticketstar/img/common/btn_delete.gif" alt="閉じる" width="16" height="16" class="helpClose" /></dd>
		</dl>
		<h2 id="help5"><img src="/static/ticketstar/img/help/title_seven.gif" alt="セブン－イレブン引取" width="742" height="43" /></h2>
		<dl class="helpList">
			<dt>会員IDを忘れてしまいました。</dt>
			<dd><img src="/static/ticketstar/img/help/icon_a.gif" alt="" width="20" height="20" class="helpAnswer" />回答が入ります。<img src="/static/ticketstar/img/common/btn_delete.gif" alt="閉じる" width="16" height="16" class="helpClose" /></dd>
			<dt>パスワードを忘れてしまいました。</dt>
			<dd><img src="/static/ticketstar/img/help/icon_a.gif" alt="" width="20" height="20" class="helpAnswer" />回答が入ります。<img src="/static/ticketstar/img/common/btn_delete.gif" alt="閉じる" width="16" height="16" class="helpClose" /></dd>
			<dt>登録している住所やメールアドレスの変更はできますか？</dt>
			<dd><img src="/static/ticketstar/img/help/icon_a.gif" alt="" width="20" height="20" class="helpAnswer" />回答が入ります。<img src="/static/ticketstar/img/common/btn_delete.gif" alt="閉じる" width="16" height="16" class="helpClose" /></dd>
		</dl>
		<!-- InstanceEndEditable -->
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
