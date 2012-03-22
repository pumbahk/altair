## summary widget dialog
##  view function is views.SummaryWidgetView.dialog
##
<!-- Summary App Interface -->
<div id="app">
  <div class="title">
    <h1>サマリー</h1>
  </div>
  <div class="content" class="float">
    <div id="create-content">
	  <table>
	  	<tr>
		  <td><label>見出し<input id="label_input" placeholder="ここに見出しを追加" type="text" /></label></td>
	  	  <td><label>内容<input id="content_input" placeholder="ここに内容を追加" type="text" /></label></td>
		</tr>
	  </table>
    </div>
	<span class="clear"/>

    <h3>現在保存されている内容</h3>
    <hr/>

    <div id="contents">
	  <table>
		<thead>
		  <tr><th>見出し</th><th>内容</th><th>削除</th></tr>
		</thead>
		<tbody id="contentlist">
		</tbody>
	  </table>
    </div>
  </div>
  <button id="submit" type="button">登録</button>
</div>
<script type="text/javascript">
(function(){
    var Item = Backbone.Model.extend({
        sync: function(){
            //don't sync this object
            return
        }, 
        defaults: function() {
            return {
                label: "見出し", 
                content: "内容", 
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
            '<td class="content"></td>', 
            '<td><a href="#" class="remove">remove</a></td>', 
        ].join("\n")), 

        events: {
            "click a.remove": "clearSelf"
        }, 

        initialize: function(){
            this.model.bind("change", this.render, this);
            this.model.bind("destroy", this.remove, this);            
        }, 
        render: function(){
            $(this.el).html(this.template(this.model.toJSON()));
            this.setContent();
            return this;
        }, 
        
        setContent: function(){
            var label = this.model.get("label");
            this.$(".label").text(label);

            var content = this.model.get("content");
            this.$(".content").text(content);
            // this.input.bind('blur', _.bind(this.close, this)).val(text);
            // blue is unfocus. todo sample is then saved object
        }, 
        clearSelf: function(){
            this.model.destroy();
        }, 
        remove: function() {
            $(this.el).remove();
        },
    });

    var AppView = Backbone.View.extend({
        // el: $("#app"), 
        initialize: function(){
            this.label_input = this.$("#label_input");
            this.content_input = this.$("#content_input");
            // model
            this.contentlist = new ItemList();
            this.contentlist.bind("add", this.addOne, this);
        }, 
        
        events: {
            "keypress #label_input": "createOnEnter", 
            "keypress #content_input": "createOnEnter", 
        }, 
        
        addOne: function(item){
            var view = new ItemView({model: item});
            $(this.el).find("#contentlist").append(view.render().el);
        }, 
        
        loadData: function(params){
            var contentlist = this.contentlist
            _(params).each(function(param){
                contentlist.create(param);
            });
        }, 

        collectData: function(){
            return _($(this.el).find("#contentlist tr")).map(function(e){
                var e = $(e);
                return {
                    label: e.find(".label").text(), 
                    content: e.find(".content").text()
                };
            });
        }, 

        createOnEnter: function(e){
            var label = this.label_input.val();
            var content = this.content_input.val();
            if (!label || !content || e.keyCode != 13) return;
            this.contentlist.create({label: label, content: content});
            this.label_input.val("");
            this.content_input.val("");
        }, 
    });

  var root =  $("#app");
  var appview = new AppView({el: root}); 
  root.data("appview",appview);
  appview.loadData($.parseJSON('${items|n}')); <%doc> items is mako </%doc>
})();
</script>
