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
        <th>会員ID</th>
        <th>有効期限</th>
        <th>有効フラグ</th>
        <th colspan="2">-</th>
      </thead>
      <tbody>
    % for membership_id, membership_form_fields in form.memberships:
    % for membership_form_field in membership_form_fields:
      <tr class="controls-table-row${u' placeholder' if membership_id == form.memberships.placeholder_subfield_name else u''}">
        <td>${membership_form_field.member_kind_id}</td>
        <td>${membership_form_field.membership_identifier}</td>
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
<div class="control-group">
  <label class="control-label" for="member-form--email">${form.email.label.text}</label>
  <div class="controls">
    ${form.email(id="member-form--email", autocomplete="off")}
    %if form.email.errors:
    <span class="help-inline">${u' / '.join(form.email.errors)}</span>
    % endif
  </div>
</div>
<div class="control-group">
  <label class="control-label" for="member-form--family_name">${form.family_name.label.text}</label>
  <div class="controls">
    ${form.family_name(id="member-form--family_name", autocomplete="off")}
    %if form.family_name.errors:
    <span class="help-inline">${u' / '.join(form.family_name.errors)}</span>
    % endif
  </div>
</div>
<div class="control-group">
  <label class="control-label" for="member-form--given_name">${form.given_name.label.text}</label>
  <div class="controls">
    ${form.given_name(id="member-form--given_name", autocomplete="off")}
    %if form.given_name.errors:
    <span class="help-inline">${u' / '.join(form.given_name.errors)}</span>
    % endif
  </div>
</div>
<div class="control-group">
  <label class="control-label" for="member-form--family_name_kana">${form.family_name_kana.label.text}</label>
  <div class="controls">
    ${form.family_name_kana(id="member-form--family_name_kana", autocomplete="off")}
    %if form.family_name_kana.errors:
    <span class="help-inline">${u' / '.join(form.family_name_kana.errors)}</span>
    % endif
  </div>
</div>
<div class="control-group">
  <label class="control-label" for="member-form--given_name_kana">${form.given_name_kana.label.text}</label>
  <div class="controls">
    ${form.given_name_kana(id="member-form--given_name_kana", autocomplete="off")}
    %if form.given_name_kana.errors:
    <span class="help-inline">${u' / '.join(form.given_name_kana.errors)}</span>
    % endif
  </div>
</div>
<div class="control-group">
  <label class="control-label" for="member-form--birthday">${form.birthday.label.text}</label>
  <div class="controls">
    ${form.birthday(autocomplete="off")}
    %if form.birthday.errors:
    <span class="help-inline">${u' / '.join(form.birthday.errors)}</span>
    % endif
  </div>
</div>
<div class="control-group">
  <label class="control-label" for="member-form--gender">${form.gender.label.text}</label>
  <div class="controls">
    ${form.gender(id="member-form--gender", autocomplete="off")}
    %if form.gender.errors:
    <span class="help-inline">${u' / '.join(form.gender.errors)}</span>
    % endif
  </div>
</div>
<div class="control-group">
  <label class="control-label" for="member-form--country">${form.country.label.text}</label>
  <div class="controls">
    ${form.country(id="member-form--country", autocomplete="off")}
    %if form.country.errors:
    <span class="help-inline">${u' / '.join(form.country.errors)}</span>
    % endif
  </div>
</div>
<div class="control-group">
  <label class="control-label" for="member-form--zip">${form.zip.label.text}</label>
  <div class="controls">
    ${form.zip(id="member-form--zip", autocomplete="off")}
    %if form.zip.errors:
    <span class="help-inline">${u' / '.join(form.zip.errors)}</span>
    % endif
  </div>
</div>
<div class="control-group">
  <label class="control-label" for="member-form--prefecture">${form.prefecture.label.text}</label>
  <div class="controls">
    ${form.prefecture(id="member-form--prefecture", autocomplete="off")}
    %if form.prefecture.errors:
    <span class="help-inline">${u' / '.join(form.prefecture.errors)}</span>
    % endif
  </div>
</div>
<div class="control-group">
  <label class="control-label" for="member-form--city">${form.city.label.text}</label>
  <div class="controls">
    ${form.city(id="member-form--city", autocomplete="off")}
    %if form.city.errors:
    <span class="help-inline">${u' / '.join(form.city.errors)}</span>
    % endif
  </div>
</div>
<div class="control-group">
  <label class="control-label" for="member-form--address_1">${form.address_1.label.text}</label>
  <div class="controls">
    ${form.address_1(id="member-form--address_1", autocomplete="off")}
    %if form.address_1.errors:
    <span class="help-inline">${u' / '.join(form.address_1.errors)}</span>
    % endif
  </div>
</div>
<div class="control-group">
  <label class="control-label" for="member-form--address_2">${form.address_2.label.text}</label>
  <div class="controls">
    ${form.address_2(id="member-form--address_2", autocomplete="off")}
    %if form.address_2.errors:
    <span class="help-inline">${u' / '.join(form.address_2.errors)}</span>
    % endif
  </div>
</div>
<div class="control-group">
  <label class="control-label" for="member-form--tel_1">${form.tel_1.label.text}</label>
  <div class="controls">
    ${form.tel_1(id="member-form--tel_1", autocomplete="off")}
    %if form.tel_1.errors:
    <span class="help-inline">${u' / '.join(form.tel_1.errors)}</span>
    % endif
  </div>
</div>
<div class="control-group">
  <label class="control-label" for="member-form--tel_2">${form.tel_2.label.text}</label>
  <div class="controls">
    ${form.tel_2(id="member-form--tel_2", autocomplete="off")}
    %if form.tel_2.errors:
    <span class="help-inline">${u' / '.join(form.tel_2.errors)}</span>
    % endif
  </div>
</div>

