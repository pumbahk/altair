<%inherit file="altaircms:templates/front/ticketstar/music.mako"/>
<%namespace file="altaircms:templates/front/ticketstar/gadgets.mako" name="gadgets"/>
##<%namespace file="./components/ticketstar/music/header.mako" name="header_co"/>
##<%namespace file="./components/ticketstar/music/userbox.mako" name="userbox_co"/>

#### variables
## subcategories
## categories
## top_ourter_categories
## top_inner_categories

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
		${widgets("side")}
  	    ${gadgets.sidebar_genre_listing(sub_categories)}

		<dl id="sideRefineSearch">
            ${gadgets.sidebar_area_listing(areas)}
            ${gadgets.sidebar_deal_cond_listing()}
			${gadgets.sidebar_deal_open_listing()}
			${gadgets.sidebar_event_open_listing()}
		</dl>

		${gadgets.sidebar_maintenance()}
		<!-- InstanceEndEditable -->
		${gadgets.sidebar_sideBtn()}
</%block>
