<%inherit file="/_base.mako" />
<%block name="title">ログイン</%block>
<style>
    body {
        background-color: #eee;
    }
</style>

<form id="signin-form" class="form-horizontal col-lg-4 col-lg-offset-4" action="${request.current_route_path(_query=dict(return_url=return_url))}" method="POST">
    <h3 class="form-heading">Famiポート運用ツール</h3>

    %for field in form:
    <div class="form-group has-feedback">
        <label class="control-label" for=${field.name}>${field.label}</label>
        ${field(class_="form-control", placeholder=field.label.text)}
    </div>
    %endfor
    <button type="submit" class="btn btn-lg btn-primary btn-block">Sign in</button>
</form>
<%block name="footer_extras">
<script src="${request.static_url('altair.app.ticketing.famiport.optool:static/js/jquery.validate.min.js')}"></script>
<script src="${request.static_url('altair.app.ticketing.famiport.optool:static/js/messages_ja.min.js')}"></script>
<script>
$("form#signin-form").validate({
    rules: {

        user_name: {
            required: true
        },

        password: {
            required: true
        },
    },

    highlight: function(element) {
        $(element).closest('.form-group').removeClass('has-success').addClass('has-error');
    },

    unhighlight: function(element) {
        $(element).closest('.form-group').removeClass('has-error').addClass('has-success');
    },

    errorElement: 'span',
    errorClass: 'help-block',
    errorPlacement: function(error, element) {
        if(element.length) {
          error.insertAfter(element);
        } else {
          error.insertAfter(element);
        }
    }
});
</script>
</%block>