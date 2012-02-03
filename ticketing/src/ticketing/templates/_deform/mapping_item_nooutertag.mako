% if not field.widget.hidden:
  <!-- mapping_item -->
  <div class="form-field-label">
    % if field.title and not field.widget.hidden:
    <label title="${field.description}" for="${field.oid}">
      ${field.title}
      % if field.required:
      <span class="required" id="req-${field.oid}">*</span>
      % endif
    </label>
    % endif
  </div>

  <div class="form-field-body">
    ${field.serialize(cstruct)|n}
    % if field.error:
    <ul class="form-field-errors">
      % for index, msg in enumerate(field.error.messages()):
      <li id="index==0 and errstr or ('error-%s-%d' % (field.oid, index))"
          class="${field.widget.error_class}">
        <p>${msg}</p>
      </li>
      % endfor
    </ul>
    % endif
  </div>
  <!-- /mapping_item -->
% endif
