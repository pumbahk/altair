<%inherit file='layout.mako'/>

<div class="row">
    <div class="alert alert-info">
	  ${message}
	</div>
    <div class="span6 offset3 well"  style="text-align:center" >
        <a class="btn btn-primary" href="${request.route_url("oauth_entry")}">Login (OAuth)</a>
    </div>
</div>
