<%inherit file="altaircms:templates/front/ticketstar/first.mako"/>
<%namespace file="./components/ticketstar/first/side.mako" name="side_co"/>
##<%namespace file="./components/ticketstar/first/header.mako" name="header_co"/>
##<%namespace file="./components/ticketstar/first/userbox.mako" name="userbox_co"/>

<%def name="widgets(name)">
  % for w in display_blocks[name]:
      ${w|n}
  % endfor
</%def>

<%block name="main">
   ${widgets("main")}
</%block>

<%block name="side">
   ${widgets("side")}
##   ${side_co.sideNav()}
   ${side_co.sideBtn()}
</%block>
