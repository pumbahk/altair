// ブラウザバック禁止
window.onunload = function() {};
history.forward();

// ブラウザバックされた場合リロードする（iPhoneはブラウザバック可能なため）
window.onpageshow = function(event) {
    if (event.persisted) {
         window.location.reload();
     }
};
