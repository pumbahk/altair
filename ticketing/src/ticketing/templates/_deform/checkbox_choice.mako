<input type="hidden" name="__start__" value="${field.name}:sequence"/>
<div class="form-widget-group">
% for index, (value, title) in enumerate(field.widget.values):
  <div class="form-widget">
    <span class="form-widget-body"><input ${value in cstruct and 'checked="checked"' or ''|n} class="checkbox ${field.widget.css_class or ''}" type="checkbox" name="checkbox" value="${value}" id="${field.oid}-${index}"/></span>
    <span class="form-widget-label"><label for="${field.oid}-${index}">${title}</label></span>
  </div>
% endfor
<input type="hidden" name="__end__" value="${field.name}:sequence"/>
</div>
