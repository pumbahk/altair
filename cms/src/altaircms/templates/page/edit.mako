<%inherit file='../layout.mako'/>
<%block name='js'>
    <script type="text/javascript" src="/static/deform/js/jquery.form.js"></script>
    <script type="text/javascript" src="/static/deform/js/deform.js"></script>
    <script type="text/javascript" src="/static/deform/js/jquery.maskedinput-1.2.2.min.js"></script>
</%block>
<%block name='style'>
    <link rel="stylesheet" href="/static/deform/css/form.css" type="text/css" />
    <style type="text/css">
        #pagelayout {
            width: 900px;
            float: left;
            background-color: #f8f8ff;
        }
        #pagewidget {
            width: 900px;
            float: left;
            background-color: #f5f5dc;
        }
        #pageversion {
            width: 300px;
            height: 150px;
            float: right;
            background-color: #faebd7;
        }
        #page {
            width: 100%;
            height: 300px;
            background-color: #adff2f;
            text-align: center;
            vertical-align: middle;
        }
    </style>
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

<div id="pagecontentform">
    <form action="${request.route_url('page_edit', event_id=event.id, page_id=page.id)}" method="post">
        <%doc>
        <div id="pagelayout">
            レイアウト選択
            <select name="layout_id">
                <option value="1">layout 1</option>
                <option value="2">layout 2</option>
            </select>
        </div>
        <div id="pageversion">ページのバージョンが入る</div>
        <div id="pagewidget">ウィジェット</div>
        <br class="clear"/>
        <div id="page">ページ編集</div>
        <button type="submit">保存</button>
</%doc>
        ${form|n}
    </form>
</div>
