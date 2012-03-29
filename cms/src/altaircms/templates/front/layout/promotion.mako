<%inherit file="altaircms:templates/front/promotion/base.mako"/>
<%def name="widgets(name)">
  % for w in display_blocks[name]:
      ${w|n}
  % endfor
</%def>

<%block name="main">
  ${widgets("main")}
</%block>

<%block name="sub">
  ${widgets("sub")}
</%block>