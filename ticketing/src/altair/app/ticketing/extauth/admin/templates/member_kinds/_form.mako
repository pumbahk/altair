<div class="control-group">
  <label class="control-label" for="member_kind-form--member_set_id">${form.member_set_id.label.text}</label>
  <div class="controls">
    ${form.member_set_id(id="member_kind-form--member_set_id")}
    %if form.member_set_id.errors:
    <span class="help-inline">${u' / '.join(form.member_set_id.errors)}</span>
    % endif
  </div>
  <label class="control-label" for="member_kind-form--name">${form.name.label.text}</label>
  <div class="controls">
    ${form.name(id="member_kind-form--name")}
    %if form.name.errors:
    <span class="help-inline">${u' / '.join(form.name.errors)}</span>
    % endif
  </div>
  <label class="control-label" for="member_kind-form--display_name">${form.display_name.label.text}</label>
  <div class="controls">
    ${form.display_name(id="member_kind-form--display_name")}
    %if form.display_name.errors:
    <span class="help-inline">${u' / '.join(form.display_name.errors)}</span>
    % endif
  </div>
  <label class="control-label" for="member_kind-form--show_in_landing_page">${form.show_in_landing_page.label.text}</label>
  <div class="controls">
    ${form.show_in_landing_page(id="member_kind-form--show_in_landing_page")}
    %if form.show_in_landing_page.errors:
    <span class="help-inline">${u' / '.join(form.show_in_landing_page.errors)}</span>
    % endif
  </div>
  <label class="control-label" for="member_kind-form--enable_guests">${form.enable_guests.label.text}</label>
  <div class="controls">
    ${form.enable_guests(id="member_kind-form--show_in_landing_page")}
    %if form.enable_guests.errors:
    <span class="help-inline">${u' / '.join(form.enable_guests.errors)}</span>
    % endif
  </div>
</div>
