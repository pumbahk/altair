<%inherit file='../layout_2col.mako'/>
<%namespace name="co" file="components.mako"/>

<h2>tag top</h2>

${co.menutab(supported)}

<div class="row">
  <div class="span5">
	<form action="#" method="GET">
      <table class="table">
        <tbody>
          ${co.formfield("classifier")}
          ${co.formfield("query")}
        </tbody>
      </table>
	  <button type="submit" class="btn btn-primary"><i class="icon-cog icon-white"></i> Search</button>
    </form>
  </div>
</div>




