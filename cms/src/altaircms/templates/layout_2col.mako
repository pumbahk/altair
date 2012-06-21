<%inherit file='layout.mako'/>
<%namespace name="nco" file="./navcomponents.mako"/>
<div class="row">
  <div class="span2"><%block name="contentleft">${nco.sidebar(request)}</%block></div>
  <div class="breadcrumbs"><%block name="breadcrumbs"/></div> 
  <div class="span12">
	<%block name="flashmessage">${nco.flashmessage("flashmessage")}</%block>
	<%block name="contentright">${self.body()}</%block>
  </div>
</div>
