<%def name="container_layout()">
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
//            height: 150px;
            float: right;
            background-color: #faebd7;
        }
        #main_page {
            width: 100%;
//            height: 300px;
            background-color: #adff2f;
            text-align: center;
            vertical-align: middle;
        }
    </style>
</%def>

<%def name="widget_css_scripts()">
 ##todo: moveit
    <link rel="stylesheet" type="text/css" href="/plugins/static/css/widget/lib/image.css">
    <link rel="stylesheet" type="text/css" href="/plugins/static/css/widget/lib/calendar.css">
</%def>