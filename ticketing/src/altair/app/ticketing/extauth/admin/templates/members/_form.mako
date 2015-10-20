<div class="control-group">
  <label class="control-label" for="member-form--enabled">${form.enabled.label.text}</label>
  <div class="controls">
    ${form.enabled(id="member-form--enabled")}
    %if form.enabled.errors:
    <span class="help-inline">${u' / '.join(form.enabled.errors)}</span>
    % endif
  </div>
</div>
<div class="control-group">
  <label class="control-label" for="member-form--member_set_id">${form.member_set_id.label.text}</label>
  <div class="controls">
    ${form.member_set_id(id="member-form--member_set_id")}
    %if form.member_set_id.errors:
    <span class="help-inline">${u' / '.join(form.member_set_id.errors)}</span>
    % endif
  </div>
</div>
<div class="control-group">
  <label class="control-label" for="member-form--name">${form.name.label.text}</label>
  <div class="controls">
    ${form.name(id="member-form--name")}
    %if form.name.errors:
    <span class="help-inline">${u' / '.join(form.name.errors)}</span>
    % endif
  </div>
</div>
<div class="control-group">
  <label class="control-label" for="member-form--auth_identifier">${form.auth_identifier.label.text}</label>
  <div class="controls">
    ${form.auth_identifier(id="member-form--auth_identifier")}
    %if form.auth_identifier.errors:
    <span class="help-inline">${u' / '.join(form.auth_identifier.errors)}</span>
    % endif
  </div>
</div>
<div class="control-group">
  <label class="control-label" for="member-form--auth_secret">${form.auth_secret.label.text}</label>
  <div class="controls">
    ${form.auth_secret(id="member-form--auth_secret", autocomplete="off")}
    %if form.auth_secret.errors:
    <span class="help-inline">${u' / '.join(form.auth_secret.errors)}</span>
    % endif
  </div>
</div>
<div class="control-group">
  <label class="control-label" for="member-form--auth_secret_confirm">${form.auth_secret_confirm.label.text}</label>
  <div class="controls">
    ${form.auth_secret_confirm(id="member-form--auth_secret_confirm", autocomplete="off")}
    %if form.auth_secret_confirm.errors:
    <span class="help-inline">${u' / '.join(form.auth_secret_confirm.errors)}</span>
    % endif
</div>
<div class="control-group memberships">
  <label class="control-label" for="member-form--memberships">${form.memberships.label.text}</label>
  <div class="controls">
    <table class="controls-table table" style="display: inline-block">
      <thead>
        <th>会員区分</th>
        <th>有効期限</th>
        <th>有効フラグ</th>
        <th colspan="2">-</th>
      </thead>
      <tbody>
    % for membership_id, membership_form_fields in form.memberships:
    % for membership_form_field in membership_form_fields:
      <tr class="controls-table-row${u' placeholder' if membership_id == form.memberships.placeholder_subfield_name else u''}">
        <td>${membership_form_field.member_kind_id}</td>
        <td>
          ${membership_form_field.valid_since}から
          ${membership_form_field.expire_at}
        </td>
        <td>
          ${membership_form_field.enabled}
        </td>
        <td>
          %if membership_form_field.errors:
          <span class="help-inline">${u' / '.join(membership_form_field.errors)}</span>
          % endif
        </td>
        <td>
          <button class="btn doRemoveRow">-</button>
        </td>
      </tr>
    % endfor
    % endfor
      </tbody>
      <tfoot>
        <tr class="controls-table-row">
          <td colspan="4"><button class="btn doAddRow">+</button></td>
        </tr>
      </tfoot>
    </table>
    <script type="text/javascript">
(function ($form) {
  (function ($addRow, $removeRow, $controlsContainer, $placeholder) {
    $placeholder = $placeholder.clone();
    function attachRemoveRowHandler($removeRow) {
      $removeRow.click(function () {
        $(this).closest('.controls-table-row').remove();
        return false;
      });
    }
    $addRow.click(function () {
      $controlsContainer.append($placeholder);
      attachRemoveRowHandler($placeholder.find('.doRemoveRow'));
      return false;
    });
    attachRemoveRowHandler($removeRow);
  })(
    $form.find('.memberships .doAddRow'),
    $form.find('.memberships .doRemoveRow'),
    $form.find('.memberships .controls-table'),
    $form.find('.memberships .controls-table .controls-table-row.placeholder').last()
  );
})($('script').last().closest('form'));
    </script>
  </div>
  <span class="help-inline">${u' / '.join(error for error in form.memberships.errors if isinstance(error, basestring))}</span>
</div>
