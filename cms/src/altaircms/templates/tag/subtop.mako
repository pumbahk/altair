<%inherit file='../layout_2col.mako'/>
<%namespace name="co" file="components.mako"/>

<h2>${classifier} tag</h2>
${co.menutab(supported, classifier)}

<div class="row">
  <div class="span5">
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

  <div class="span5">
    <h3> 最近追加されたタグ</h3>
    ${co.new_tags(classifier, new_tags)}
  </div>
</div>