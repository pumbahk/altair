<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html lang="en">
<head>
  <meta http-equiv="Content-Type" content="text/html;charset=UTF-8">
  <title>ExtAuth admin</title>
  <style type="text/css">
body {
  padding-top: 60px; /* 60px to make the container go all the way to the bottom of the topbar */
}

.paid {
  background-color: #ff8;
}

.canceled {
  color: #ddd;
}
</style>
  <script type="text/javascript">
var renderConfirmationModal = null,
    bsConfirm = null;
(function () {
var confirmationModal = null;
var confirmationModalCallback = null;
var confirmationModalShown = false;
var confirmationModalHiddenCallback = null;

renderConfirmationModal = function renderConfirmationModal() {
  if (confirmationModal === null) {
    confirmationModal = $('<div class="modal hide" role="modal" id="confirmation-modal"><div class="modal-header"><button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button><h3 class="modal-title"></h3></div><div class="modal-body"></div><div class="modal-footer"><button type="button" class="btn primary prompt-yes">はい</button><button type="button" class="btn prompt-no">いいえ</button></div></div>');
    confirmationModal.find('.modal-footer .prompt-yes, .modal-footer .prompt-no').on('click', function (e) {
      var yes = this.className.indexOf('prompt-yes') >= 0;
      confirmationModalHiddenCallback = function () {
        if (confirmationModalCallback) {
          if (yes) {
            return confirmationModalCallback.call(this, true, e);
          } else {
            return confirmationModalCallback.call(this, false, e);
          }
        }
      };
      confirmationModal.modal('hide');
    });
    confirmationModal.on('shown', function () {
      confirmationModalShown = true;
      confirmationModalHiddenCallback = function () {
        if (confirmationModalCallback) {
          return confirmationModalCallback.call(this, false, null);
        }
      };
    });
    confirmationModal.on('hidden', function () {
      confirmationModalShown = false;
      if (confirmationModalHiddenCallback) {
        var _confirmationModalHiddenCallback = confirmationModalHiddenCallback;
        confirmationModalHiddenCallback = null;  
	_confirmationModalHiddenCallback.call(this);
      }
    });
    confirmationModal.appendTo(document.body);
  }
  return confirmationModal;
};

bsConfirm = function bsConfirm(body, callback, options) {
  if (confirmationModalShown)
    return null;
  _options = { title: '', yesButtonLabel: 'はい', noButtonLabel: 'いいえ' };
  $.extend(_options, options);
  var confirmationModal = renderConfirmationModal();
  if (_options.title) {
    confirmationModal.find('.modal-header').css('display', 'block');
    confirmationModal.find('.modal-title').text(_options.title);
  } else {
    confirmationModal.find('.modal-header').css('display', 'none');
  }
  confirmationModal.find('.modal-body').empty().append($('<p></p>').text(body));
  confirmationModal.find('.modal-footer .prompt-yes').text(_options.yesButtonLabel);
  confirmationModal.find('.modal-footer .prompt-no').text(_options.noButtonLabel);
  confirmationModalCallback = callback;
  confirmationModal.modal('show');
};
})();
$(function () {
  renderConfirmationModal();
  var nodes = $('input[type="submit"],button[type="submit"]');
  nodes.each(function (_, n) {
    n = $(n);
    var submitConfirmationPrompt = n.data('submitConfirmationPrompt');
    if (submitConfirmationPrompt) {
      var inner = false;
      n.on('click', function (e) {
        if (!inner) {
          e.preventDefault();
          inner = true;
          bsConfirm(submitConfirmationPrompt, function (yes) {
            if (yes) {
	      $(n.get(0)).click();
            } else {
              inner = false;
            }
          });
        } else {
          inner = false;
        }
      });
    }
  });
});
</script>
</head>
<body>
  <div class="navbar navbar-fixed-top">
    <div class="navbar-inner">
      <div class="container">
        <a class="brand" href="${request.route_path('top')}">ExtAuth admin</a>
        <div class="nav-collapse">
          <ul class="nav pull-right">
            % if request.operator is not None:
            <li><a href="${request.route_path('logout')}"><i class="icon-off"></i> ログアウト</a></li>
            % endif
          </ul>
        </div><!--/.nav-collapse -->
      </div>
    </div>
  </div>
  <div class="container">
    ${next.body()}
  </div>
</body>
</html>
<!--
vim: sts=2 sw=2 ts=2 et
-->
