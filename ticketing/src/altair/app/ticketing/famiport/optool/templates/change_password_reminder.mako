<%inherit file="/_base.mako" />
<%block name="title">パスワード変更</%block>
<style>
    body {
        background-color: #eee;
    }
</style>

<form id="change-password-form" class="form-horizontal" action="${action_url}" method="POST" autocomplete="off">
    <h3 class="form-heading">パスワード再設定</h3>
    <p class="bg-danger">パスワードは数字と英文字の両方を含む7文字以上で設定ください。</p>
    <p class="bg-danger">使える記号は「~!@#$%^&*()_+-=[]{}|;:<>?,./」のみです。</p>
    %for field in form:
    <div class="form-group has-feedback">
        % if field.widget.input_type != 'hidden':
            <label class="control-label" for=${field.name}>${field.label}</label>
            ${field(class_="form-control", placeholder=field.label.text)}
        % else:
            ${field}
        %endif
    </div>
    %endfor
    <br />
    <button type="submit" class="btn btn-lg btn-primary btn-block">登録</button>
</form>

<%block name="footer_extras">
<script src="${request.static_url('altair.app.ticketing.famiport.optool:static/js/jquery.validate.min.js')}"></script>
<script src="${request.static_url('altair.app.ticketing.famiport.optool:static/js/messages_ja.min.js')}"></script>
<script>
// クライアント側のバリデーション
$("form#change-password-form").validate({
    rules: {
        email: {
            required: true,
            email: true
        },

        new_password: {
            minlength: 7,
            required: true,
            password_rule: true
        },

        new_password_confirm: {
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
jQuery.validator.addMethod('password_rule', function (val) {
  var pattern = /^(?=.*[a-zA-Z])(?=.*[0-9])([A-Za-z0-9\~\!\@\#\$\%\^\&\*\(\)\_\+\-\=\[\]\{\}\|\;\:\<\>\?\,\.\/]+)$/
  if (!pattern.test(val)) {
    return false;
  } else {
    return true
  }
}, "半角英数字混在でご入力下さい。（使用可能な記号については表記の通りです）");
</script>
</%block>
