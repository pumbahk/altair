<%inherit file="altaircms:templates/front/ticketstar/top.mako"/>
<%namespace file="./components/ticketstar/top/main.mako" name="main_co"/>
<%namespace file="./components/ticketstar/top/side.mako" name="side_co"/>

<%def name="widgets(name)">
  % for w in display_blocks[name]:
      ${w|n}
  % endfor
</%def>

<%block name="main">
   ${widgets("main")}
## <hr/><hr/><hr/><hr/><hr/><hr/>
##        ${main_co.slideShow()}
##        ${main_co.topics()}
##        ${main_co.events()}
##        ${main_co.thisWeek()}
##        ${main_co.nearTheEnd()}
        ${main_co.checkEvent()}
</%block>

<%block name="main_left">
   ${widgets("main_left")}
</%block>
<%block name="main_right">
   ${widgets("main_right")}
</%block>
<%block name="main_bottom">
   ${widgets("main_bottom")}
   ${main_co.eventRecommend()}
</%block>

<%block name="side">
        ${side_co.sideFeature()}
        ${side_co.sideSearch()}
        ${side_co.sideMyMenu()}
        ${side_co.sideInfo()}
        ${side_co.sideBtn()}
        ${side_co.facebook()}
        ${side_co.twitter()}
</%block>
