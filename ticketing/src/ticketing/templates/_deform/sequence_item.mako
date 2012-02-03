% if not field.widget.hidden:
<div class="form-fieldseq-field ${field.error and field.widget.error_class or ''}" ${field.description and 'title="%s"' % field.description or ''|n}>
  <!-- sequence_item -->
  ${field.serialize(cstruct)|n}
  <span class="deformClosebutton"
        id="${field.oid}-close"
        title="Remove"
        onclick="javascript:deform.removeSequenceItem(this);"></span>
  % if field.error:
    <ul class="form-field-errors">
    % for index, msg in enumerate(field.error.messages()):
      <li id="${'error-%s-%s' % (field.oid, index)}" class="${field.widget.error_class}">${msg}</p>
    % endfor
  % endif
  <!-- /sequence_item -->
</div>
% endif
