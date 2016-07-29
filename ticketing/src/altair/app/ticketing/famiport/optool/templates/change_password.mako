<%inherit file="/_base.mako" />
<%block name="title">パスワード変更</%block>
<style>
    body {
        background-color: #eee;
    }
</style>

<form id="change-password-form" class="form-horizontal" action="${request.route_url('change_password')}" method="POST">
    <h3 class="form-heading">パスワード変更</h3>
    %for field in form:
    <div class="form-group has-feedback">
        %if field.widget.input_type != 'hidden':
        <label class="control-label" for=${field.name}>${field.label}</label>
        %endif
        ${field(class_="form-control", placeholder=field.label.text)}
    </div>
    %endfor
    <br />
    <button type="submit" class="btn btn-lg btn-primary btn-block">Send</button>
</form>

<%block name="footer_extras">
<script src="${request.static_url('altair.app.ticketing.famiport.optool:static/js/jquery.validate.min.js')}"></script>
<script src="${request.static_url('altair.app.ticketing.famiport.optool:static/js/messages_ja.min.js')}"></script>
<script>
$("form#change-password-form").validate({
    rules: {
        password: {
            required: true
        },

        new_password: {
            minlength: 7,
            required: true
        },

        new_password_confirm: {
            required: true,
            equalTo: "#new_password"
        }
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
