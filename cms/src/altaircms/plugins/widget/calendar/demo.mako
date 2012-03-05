<!-- <p>select: ${calendar_type}</p> -->
sample表示

<dl>
  <dt>説明</dt>
  <dd>${description}</dd>
</dl>

% if form:
  <div id="select_form">
  %for field in form:
    <tr>
      %if field.type == "BooleanField":
        <td></td>
        <td>${field} ${field.label}</td>
      %else:
        <td>${ field.label }</td>
        <td>${ field }
      %endif
    </tr>
  %endfor
  </div>
% endif

${renderable.render()|n}
