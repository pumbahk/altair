<%inherit file="altaircms:templates/front/ticketstar/top.mako"/>
<%namespace file="./components/ticketstar/top/main.mako" name="main_co"/>
<%namespace file="./components/ticketstar/top/side.mako" name="side_co"/>

<%block name="main">
        ${main_co.slideShow()}
        ${main_co.topics()}
        ${main_co.events()}
        ${main_co.eventRecommend()}
        ${main_co.thisWeek()}
        ${main_co.nearTheEnd()}
        ${main_co.checkEvent()}
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
