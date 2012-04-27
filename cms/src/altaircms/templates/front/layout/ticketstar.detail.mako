<%inherit file="altaircms:templates/front/ticketstar/detail.mako"/>
<%namespace file="./components/ticketstar/detail/header.mako" name="header_co"/>
## <%namespace file="./components/ticketstar/detail/main.mako" name="main_co"/>
## <%namespace file="./components/ticketstar/detail/side.mako" name="side_co"/>
<%namespace file="./components/ticketstar/detail/userbox.mako" name="userbox_co"/>

## <%block name="css_prerender">
## </%block>

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
   ${widgets("main")}
</%block>


<%block name="side">
    ${widgets("side")}
</%block>


<%block name="userBox">
   ${userbox_co.userbox()}
</%block>
