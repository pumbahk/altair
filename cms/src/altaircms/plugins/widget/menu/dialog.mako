## menu widget dialog
##  view function is views.MenuWidgetView.dialog
##
<!-- Menu App Interface -->
<div id="app">
  <div class="title">
    <h1>メニュータブ</h1>
  </div>
  <div class="content" class="float">
    <div id="create-menu">
	  <table>
	  	<tr>
		  <td><label>リンク先名<input id="label_input" placeholder="ここにリンク名を追加" type="text" /></label></td>
	  	  <td><label>URL<input id="link_input" placeholder="ここにリンク先のURLを追加" type="text" /></label></td>
		</tr>
	  </table>
    </div>
	<span class="clear"/>

    <h3>現在保存されているタブ</h3>
    <hr/>

    <div id="menus">
	  <table>
		<thead>
		  <tr><th>リンク先名</th><th>URL</th><th>削除</th></tr>
		</thead>
		<tbody id="menulist">
		</tbody>
	  </table>
    </div>
  </div>
  <button id="submit" type="button">登録</button>
</div>
<script type="text/javascript">
<%text>
(function(){
    var Item = Backbone.Model.extend({
        sync: function(){
            //don't sync this object
            return
        }, 
        defaults: function() {
            return {
                label: "リンク名", 
                link: "URL", 
                order: 0, 
            };
        },
    });

    var ItemList = Backbone.Collection.extend({
        model: Item, 
        nextOrder: function(){
            if (!this.length) return 1;
            return this.last().get("order") + 1;
        }, 
        
        comparator: function(item){
            return item.get("order");
        }
    });

    var ItemView = Backbone.View.extend({
        tagName: "tr", 
        className: "item", 
        template: _.template([
            '<td class="label"></td>', 
            '<td class="link"></td>', 
            '<td><a href="#" class="remove">remove</a></td>', 
        ].join("\n")), 

        events: {
            "click a.remove": "clearSelf", 
            "dblclick td": "transformEditView"
        }, 

        initialize: function(){
            this.model.bind("change", this.render, this);
            this.model.bind("destroy", this.remove, this);            
            this.model.bind("redraw", this.render, this);
        }, 

        render: function(){
            $(this.el).html(this.template(this.model.toJSON()));
            this.setContent();
            return this;
        }, 
        
        setContent: function(){
            var label = this.model.get("label");
            this.$(".label").text(label);

            var link = this.model.get("link");
            this.$(".link").html($("<a>").attr("href",link).text(link));
            // this.input.bind('blur', _.bind(this.close, this)).val(text);
            // blue is unfocus. todo sample is then saved object
        }, 
        clearSelf: function(){
            this.model.destroy();
        }, 
        transformEditView: function(){
            this.model.unbind("change", this.render);
            var edit_view = new EditItemView({model: this.model});
            $(this.el).html(edit_view.render().el);
        }, 
        remove: function() {
            $(this.el).remove();
        },
    });

    var EditItemView = Backbone.View.extend({
        tagName: "div", 
        className: "edit-item", 
        template: _.template([
       			'<td><label>リンク先名<input class="label" type="text" value="<%= label %>"/></label></td>', 
            '<td><label>URL<input class="link" type="text" value="<%= link %>"/></label></td>'
        ].join("\n")), 
        
        events: {
            "keypress .label": "updateOnEnter", 
            "keypress .link": "updateOnEnter", 
        }, 

        updateOnEnter: function(e){
            var label = this.$(".label").val();
            var link = this.$(".link").val();
            if (!label || !link || e.keyCode != 13) return;
            this.model.set("label", label);
            this.model.set("link", link);
            this.yank();
        }, 

        yank: function(){
            this.remove();
            this.model.trigger("redraw");
        }, 

        render: function(){
            $(this.el).html(this.template(this.model.toJSON()));
            return this;
        }
    });

    var AppView = Backbone.View.extend({
        // el: $("#app"), 
        initialize: function(){
            this.label_input = this.$("#label_input");
            this.link_input = this.$("#link_input");
            // model
            this.menulist = new ItemList();
            this.menulist.bind("add", this.addOne, this);
        }, 
        
        events: {
            "keypress #label_input": "createOnEnter", 
            "keypress #link_input": "createOnEnter", 
        }, 
        
        addOne: function(item){
            var view = new ItemView({model: item});
            $(this.el).find("#menulist").append(view.render().el);
        }, 
        
        loadData: function(params){
            var menulist = this.menulist
            _(params).each(function(param){
                menulist.create(param);
            });
        }, 

        collectData: function(){
			var get_text_or_val = function(e,expr){ 
			  var e = e.find(expr);
			  return e.text() || e.val();
			}
            return _($(this.el).find("#menulist tr")).map(function(e){
                var e = $(e);
                return {
                    label: get_text_or_val(e, ".label"),
                    content: get_text_or_val(e, ".link")
                };
            });
        }, 

        createOnEnter: function(e){
            var label = this.label_input.val();
            var link = this.link_input.val();
            if (!label || !link || e.keyCode != 13) return;
            this.menulist.create({label: label, link: link});
            this.label_input.val("");
            this.link_input.val("");
        }, 
    });
</%text>
  var root =  $("#app");
  var appview = new AppView({el: root}); 
  root.data("appview",appview);
  appview.loadData($.parseJSON('${items|n}')); <%doc> items is mako </%doc>
})();
</script>
