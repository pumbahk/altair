<%inherit file='../../layout.mako'/>

<%def name="form_column(form,k)">
  <div class="control-group">
    <label class="control-label">${getattr(form,k).label}</label>
    <div class="controls">${getattr(form,k)}
	%if k in form.errors:
      <br/>
      <br/>
	  %for error in form.errors[k]:
		<span class="alert alert-error">${error}</span>
	  %endfor
	%endif
    </div>
  </div>
</%def>

<div class="offset3">
  <div class="page-header">
    <h1>ログイン(cms)</h1>
  </div>

  <div style="width:600px;">   
    <a href="${request.route_url("login")}">戻る</a>

    <div class="well" style="text-align:center" >
    <div id="login1" style="margin-top: 30px;">
      <form class="form-horizontal" action="${request.current_route_url(action="login")}" method="POST">
        <fieldset>
          ${form_column(form,"organization_id")}
          ${form_column(form,"name")}
          ${form_column(form,"password")}
        </fieldset>
        <div class="spacer" style="width: 100px; margin: 0pt auto;">
          <input highlight="  HintElem" class="btn btn-primary" name="submit" value="ログイン" type="submit">
        </div>
      </form>
      <div class="pull-right">
        <!--<a href="/login/reset">パスワードリセット</a>-->
      </div>
    </div>
    </div>
  </div>
</div>
