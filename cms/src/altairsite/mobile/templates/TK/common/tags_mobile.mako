<%def name="band(bgcolor='#cc0000', color='#ffffff')">
<div style="background-color:${bgcolor}" bgcolor="${bgcolor}">
% if color:
<font color="${color}">
% endif
${caller.body()}
% if color:
</font>
% endif
</div>
</%def>
<%def name="header(markercolor='#cc0000')">
<div><font color="${markercolor}">■</font>${caller.body()}</div>
</%def>
<%def name="line(width=1,color='#cc0000')">
<div
% if color:
  style="background-color:${color}" bgcolor="${color}"
% endif
><img src="${request.mobile_static_url('altaircms:static/TK/mobile/clear.gif')}" width="1" height="${width}" /></div>
</%def>
