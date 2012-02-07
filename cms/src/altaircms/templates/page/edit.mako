##
##
##
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

%if page:
<h1>イベント${event}の${page}の編集</h1>
%else:
<h1>イベント${event}のページ追加</h1>
%endif
<a href="${request.route_url('event', id=event.id)}">back</a>

<div id="pageform">
    %if page:
    <form id="deform" class="deform" action="${request.route_url('page_edit', event_id=event.id, page_id=page.id)}" method="post">
    %else:
    <form id="deform" class="deform" action="${request.route_url('page_add', event_id=event.id)}" method="post">
    %endif
    ${form|n}
    </form>
</div>


<div id="pagecontentform">
    <div id="pagelayout">レイアウト選択</div>
    <div id="pageversion">ページのバージョンが入る</div>
    <div id="pagewidget">ウィジェット</div>
    <br class="clear"/>
    <form action="#" method="post">
        <div id="page">ページ編集</div>
        <button type="submit">保存</button>
    </form>
</div>
