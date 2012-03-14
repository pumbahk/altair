<%inherit file='layout.mako'/>
<div class="row">
  <div class="span2"><%block name="contentleft"><%include file="parts/sidebar.mako"/></%block></div>
  <div class="breadcrumbs"><%block name="breadcrumbs"/></div> 
  <div class="span10"><%block name="contentright">${self.body()}</%block></div>
</div>


