<%inherit file="/_base.mako" />
<%block name="title">アカウントリマインダー</%block>
<style>
    body {
        background-color: #eee;
    }
</style>

<div class="row">
<form id="account-reminder-form" class="form-horizontal" action="${request.route_url('account_reminder')}" method="POST">
    <h3 class="form-heading">アカウントリマインダー</h3>
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
</div>

<div class="row" style="text-align: center;">
<p class="extra-info-str"><a href="${request.route_path('login')}">ログインへ</a></p>
</div>

<!--
%if reminder_url:
<a href="${reminder_url}">reminder_url</a>
%endif
-->
<%block name="footer_extras">
<script src="${request.static_url('altair.app.ticketing.famiport.optool:static/js/jquery.validate.min.js')}"></script>
<script src="${request.static_url('altair.app.ticketing.famiport.optool:static/js/messages_ja.min.js')}"></script>
<script>
$("form#change-password-form").validate({
    rules: {
        user_name: {
            required: true
        },

        email: {
            maxlength: 120,
            required: true
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
