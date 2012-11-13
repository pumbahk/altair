<%inherit file='../../layout.mako'/>
<script type="text/javascript">
  $(function(){ $("#login").focus();});
</script>

<div class="offset3">
  <div class="page-header">
    <h1>まだログインしてません</h1>
  </div>
  <div style="width:600px;">
    <div class="alert alert-info" style="text-align:center">
      ${message}
    </div>
    
    <div class="well" style="text-align:center" >
      <a id="login" class="btn btn" href="${request.route_url("login.self", action="input")}">Login (self)</a>
      <a id="login" class="btn btn-primary" href="${request.route_url("oauth_entry")}">Login (OAuth)</a>
    </div>
  </div>
</div>
