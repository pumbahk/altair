##<form id="event_add_form" action="${request.route_url("api_event")}?html=t" method="PUT">
<form id="event_add_form" action="${request.route_url("event_list")}?html=t" method="POST">
  <table class="table">
    <tbody>
      <tr><th>${form.title.label}</th><td>${form.title}
      %if 'title' in form.errors:
      <br/>
      %for error in form.errors['title']:
      <span class="btn btn-warning">${error}</span>
      %endfor
      %endif
      </td></tr>
      <tr><th>${form.subtitle.label}</th><td>${form.subtitle}
            %if 'subtitle' in form.errors:
            <br/>
            %for error in form.errors['subtitle']:
            <span class="btn btn-warning">${error}</span>
            %endfor
            %endif
      </td></tr>
      <tr><th>${form.description.label}</th><td>${form.description}
            %if 'description' in form.errors:
                  <br/>
                  %for error in form.errors['description']:
                  <span class="btn btn-warning">${error}</span>
                  %endfor
                  %endif
      </td></tr>
      <tr><th>${form.inquiry_for.label}</th><td>${form.inquiry_for}
            %if 'inquiry_for' in form.errors:
                  <br/>
                  %for error in form.errors['inquiry_for']:
                  <span class="btn btn-warning">${error}</span>
                  %endfor
                  %endif
            </td></tr>
      <tr><th>${form.event_open.label}</th><td>${form.event_open} - ${form.event_close}
      %if 'event_open' in form.errors:
      <br/>
      %for error in form.errors['event_open']:
      <span class="btn btn-warning">${error}</span>
      %endfor
      %endif
      </td></tr>
      <tr><th>${form.deal_open.label}</th><td>${form.deal_open} - ${form.deal_close}
      %if 'deal_open' in form.errors:
      <br/>
      %for error in form.errors['deal_open']:
      <span class="btn btn-warning">${error}</span>
      %endfor
      %endif
      </td></tr>
      <tr><th>${form.place.label}</th><td>${form.place}
            %if 'place' in form.errors:
                  <br/>
                  %for error in form.errors['place']:
                  <span class="btn btn-warning">${error}</span>
                  %endfor
                  %endif
            </td></tr>
      <tr><th>${form.is_searchable.label}</th><td>${form.is_searchable}</td></tr>
    </tbody>
  </table>
  <button type="submit" class="btn">保存</button>
</form>
