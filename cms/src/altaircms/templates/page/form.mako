<%inherit file='../layout.mako'/>
<%block name='js'>
    <script type="text/javascript" src="/static/deform/js/jquery.form.js"></script>
    <script type="text/javascript" src="/static/deform/js/deform.js"></script>
    <script type="text/javascript" src="/static/deform/js/jquery.maskedinput-1.2.2.min.js"></script>
</%block>
<%block name='style'>
    <link rel="stylesheet" href="/static/deform/css/form.css" type="text/css" />
</%block>
<%block name='js_foot'>
    <script type="text/javascript">
        var stylesheets = ['/static/deform/css/beautify.css'];

        function deform_ajaxify(response, status, xhr, form, oid, mthd){
            var options = {
                target: '#' + oid,
                replaceTarget: true,
                success: function(response, status, xhr, form){
                    deform_ajaxify(response, status, xhr, form, oid);
                }
            };
            var extra_options = {};
            var name;
            if (extra_options) {
                for (name in extra_options) {
                    options[name] = extra_options[name];
                };
            };
            $('#' + oid).ajaxForm(options);
            if(mthd){
                mthd(response, status, xhr, form);
            }
        }
        deform.addCallback(
                'deform',
                function(oid) {
                    deform_ajaxify(null, null, null, null, oid);
                }
        );
        deform.load();
    </script>
</%block>

<h1>ページ追加 / 編集</h1>

<div id="pageform">
    <form id="deform" class="deform" action="/page/edit" method="post">
        ${form|n}
    </form>
</div>

<div id="pagecontentform">
    <form action="#" method="post">
        バージョン
        <div>レイアウト選択</div>
        <div>アセットエリア（スタイル（CSS）, ウィジェット一覧）</div>
        <div>D&amp;D UI</div>
        <button type="submit">保存</button>
    </form>
</div>