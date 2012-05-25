<%inherit file="altaircms:templates/front/ticketstar/event.mako"/>
<%namespace file="altaircms:templates/front/ticketstar/gadgets.mako" name="gadgets"/>

##<%namespace file="./components/ticketstar/event/header.mako" name="header_co"/>
##<%namespace file="./components/ticketstar/event/userbox.mako" name="userbox_co"/>

<%def name="widgets(name)">
  % for w in display_blocks[name]:
      ${w|n}
  % endfor
</%def>

<%block name="main">
   ${widgets("main")}
</%block>

<%block name="main_left">
   ${widgets("main_left")}
</%block>
<%block name="main_right">
   ${widgets("main_right")}
</%block>

<%block name="side">
		<!-- InstanceBeginEditable name="side" -->
		<!-- InstanceBeginEditable name="side" -->
		<div class="sideCategoryGenre">
		<h2>特集</h2>
		<ul>
			<li><a href="#">特集/ライブハウスへ行こう!!</a></li>
			<li><a href="#">ロックフェス特集</a></li>
			<li><a href="#">アニメぴあ</a></li>
		</ul>
		</div>

		${gadgets.sidebar_genre_listing(sub_categories)}

		<dl id="sideRefineSearch">
            ${gadgets.sidebar_area_listing(areas)}
            ${gadgets.sidebar_deal_cond_listing()}
			${gadgets.sidebar_deal_term_listing()}
			${gadgets.sidebar_performance_term_listing()}
		</dl>

		${gadgets.sidebar_maintenance()}
		<!-- InstanceEndEditable -->
		${gadgets.sidebar_sideBtn()}
</%block>
