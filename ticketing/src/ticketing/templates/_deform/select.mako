<select name="${field.name}" id="${field.oid}"
        ${field.widget.size and 'size="%s"' % field.widget.size or ''|n}>
  % for value, description in field.widget.values:
  <option ${value == cstruct and 'selected="selected"' or ''|n}
          ${field.widget.css_class and 'class="%s"' % field.widget.css_class or ''|n} value="${value}">${description}</option>
  % endfor
</select>
