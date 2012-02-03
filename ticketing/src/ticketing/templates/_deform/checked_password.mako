<input type="hidden" name="__start__" value="${field.name}:mapping"/>
<div class="form-fieldgroup">
  <div class="form-fieldgroup-fields">
    <div class="form-field">
      <div class="form-field-label">
        <label for="${field.oid}" i18n:translate="">Password</label>
      </div>
      <div class="form-field-body">
        <input type="password" name="value" value="${cstruct}"
               class="text-field ${field.widget.css_class or ''}"
               ${field.widget.size and 'size="%s"' % field.widget.size or ''|n} id="${field.oid}"/>
      </div>
    </div>
    <div class="form-field">
      <div class="form-field-label">
        <label for="${field.oid}-confirm">Confirm Password</label>
      </div>
      <div class="form-field-body">
        <input type="password" name="confirm" value="${confirm}"
               class="text-field ${field.widget.css_class or ''}"
               ${field.widget.size and 'size="%s"' % field.widget.size or ''|n}
               id="${field.oid}-confirm"/>
      </div>
    </div>
  </div>
</div>
<input type="hidden" name="__end__" value="${field.name}:mapping"/>
