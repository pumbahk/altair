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

<h1>ページ追加・一覧</h1>

<div id="pageform">
    ${form|n}
</div>

<ul>
%for page in pages:
<li><a href="${request.route_url("page_edit_", page_id=page.id)}">${page}</a></li>
%endfor
</ul>