<%inherit file="/_base.mako" />
<h1>発券完了</h1>
<p>${message}</p>
% if images:
% for image in images:
<img src="${h.to_data_scheme(image)}" />
% endfor
% endif
