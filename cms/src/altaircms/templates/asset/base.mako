<%inherit file='../layout_2col.mako'/>

<%block name="contentright">
<div class="row">
    <div class="span10">
        <ul class="breadcrumb">
            <li><a href="${request.route_path("asset_list")}">アセット</a> <span class="divider">/</span></li>
            <li>${asset.filepath}</li>
        </ul>
    </div>
</div>

${next.body()}
</%block>
