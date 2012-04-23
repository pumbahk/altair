<%inherit file="altaircms:templates/front/ticketstar/detail.mako"/>
<%namespace file="./components/ticketstar/detail/header.mako" name="header_co"/>
## <%namespace file="./components/ticketstar/detail/main.mako" name="main_co"/>
## <%namespace file="./components/ticketstar/detail/side.mako" name="side_co"/>
<%namespace file="./components/ticketstar/detail/userbox.mako" name="userbox_co"/>

<%block name="css_prerender">
  <style type="text/css">
    #detailSchedule tbody td{
      height: 59px;
    }

	#detailSchedule th.month-col {
	  width: 20px;
    }

    #ticketIcon li{
	  background-repeat: no-repeat;
	  width: 80px;
	  height: 30px;
    }
	#ticketIcon li.select {
	  background-image: url(/static/ticketstar/img/detail/icon_select.gif);
	}
	#ticketIcon li.keep {
	  background-image: url(/static/ticketstar/img/detail/icon_keep.gif);
	}
	#ticketIcon li.official {
	  background-image: url(/static/ticketstar/img/detail/icon_official.gif);
	}
	#ticketIcon li.goods {
	  background-image: url(/static/ticketstar/img/detail/icon_goods.gif);
	}
	#ticketIcon li.event {
	  background-image: url(/static/ticketstar/img/detail/icon_event.gif);
	}
  </style>
</%block>

<%def name="widgets(name)">
  % for w in display_blocks[name]:
      ${w|n}
  % endfor
</%def>

## header
<%block name="header">
	<%block name="subCategoryMenuList">
	  ${header_co.sub_category_menu_list()}
	</%block>

	<%block name="topicPath">
     ${widgets("topicPath")}
	</%block>
    ${self.inherits.header()}
</%block>


<%block name="main">
<ul id="ticketIcon">
  % for icon_class in page.service_info_list:
    <li class="${icon_class}"/>    
  % endfor
</ul>
      ${widgets("main")}
</%block>


<%block name="side">
    ${widgets("side")}
</%block>


<%block name="userBox">
   ${userbox_co.userbox()}
</%block>
