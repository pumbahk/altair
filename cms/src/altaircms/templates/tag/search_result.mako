<%inherit file='../layout_2col.mako'/>
<%namespace name="co" file="components.mako"/>

<h2>tag 検索結果 : ${request.GET["query"]}</h2>

${co.menutab(supported, classifier)}

<div class="row">
  <div class="span10">
	<form action="#" method="GET">
      <table class="table">
        <tbody>
          ${co.formfield(form, "classifier")}
          ${co.formfield(form, "query")}
        </tbody>
      </table>
	  <button type="submit" class="btn btn-primary"><i class="icon-cog icon-white"></i> Search</button>
    </form>
  </div>
</div>

<h3> 検索結果一覧 (query: ${request.GET["query"]})</h3>
<div class="row">
  <div class="span10">
    <table class="table">
	  ## これひどい
	  ${getattr(co, classifier+"_search_result")(request, query_result)}
    </table>
  </div>
</div>




