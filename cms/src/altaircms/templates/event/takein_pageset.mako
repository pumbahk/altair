<%inherit file='../layout_2col.mako'/>

<%namespace name="fco" file="../formcomponents.mako"/>


<div class="row">
    <h3>配下のページとして取り込む</h3>
	<p>${event.title}の配下のページとして取り込む</p>
    <form action="#" method="POST">
       ${fco.form_as_table_strict(form, ["pageset"])}
        <button class="btn" type="submit">配下のページとして取り込む</button>
    </form>
</div>
