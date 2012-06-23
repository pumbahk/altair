## summary widget dialog
##  view function is views.SummaryWidgetView.dialog
##
<!-- Summary App Interface -->
<div id="app">
  <div class="title">
    <h1>サマリー</h1>
    <p>購入画面では、開催期間、販売期間、会場の項目はシステム側で自動で追加されます。
       そのため、重複して表示されないよう通知をオフにしてください
    </p>  
  </div>
  <hr/>
  <div class="content" class="float">
    <div id="create-content">
   <table class="table">
           <tr>
                 <td><label>見出し<input id="label_input" placeholder="ここに見出しを追加" type="text" /></label></td>
                   <td><label>内容<textarea width="300px" id="content_input" placeholder="ここに内容を追加" type="text" /></textarea></label></td>
                   <td><label>購入ページに通知する<input id="notify_input"  type="checkbox" checked="checked"/></label></td>
                 <td><button id="additem_button" type="button" class="btn">追加する</button></td>
          </tr>
      </table>
    </div>
    <span class="clear"/>

    <h3>現在保存されている内容</h3>
    <hr/>

    <div id="contents">
      <button class="btn" type="button" id="reflesh_button">最初の状態に戻す</button>
      <button class="btn" type="button" url="${request.route_path("api_summary_widget_data_from_db")}" id="load_from_api_button">登録されたデータから内容を取得</button>
      <button id="removeall_button" type="button" class="btn">全部削除</button>
      <button id="summary_submit" type="button" class="btn btn-primary">登録</button>

      <table id="item-result"width="100%">
        <thead>
          <tr><th>見出し</th><th>内容</th><th>通知</th><th>削除</th></tr>
        </thead>
        <tbody id="contentlist">
        </tbody>
      </table>
    </div>
  </div>
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
            '<td><input type="checkbox" class="notify"/></td>', 
            '<td><a href="#" class="remove">remove</a></td>', 
        ].join("\n")), 

        events: {
            "click a.remove": "clearSelf",
            "dblclick td": "transformEditView"
        }, 

        initialize: function(){
            this.model.bind("change", this.render, this);
            this.model.bind("destroy", this.remove, this);            
            this.model.bind("redraw", this.reDraw, this);
        }, 

        
        render: function(){
            $(this.el).html(this.template(this.model.toJSON()));
            this.setContent();
            return this;
        }, 
        
        reDraw: function(me){
            $(this.el).css("display","table-row");
            this.setContent();
        },
        setContent: function(){
            var label = this.model.get("label");
            this.$(".label").text(label);

            var content = this.model.get("content");
            this.$(".content").text(content);
            if(this.model.get("notify")){
              this.$(".notify").attr("checked","checked");
            }
            // this.input.bind('blur', _.bind(this.close, this)).val(text);
            // blue is unfocus. todo sample is then saved object
        }, 
        clearSelf: function(e){
            this.model.destroy();
            e.preventDefault();
        }, 
        transformEditView: function(){
            this.model.unbind("change", this.render);
            $(this.el).css("display","none");
            var edit_view = new EditItemView({model: this.model, view: this});
            $(this.el).after(edit_view.render().el);
        }, 
        remove: function() {
            $(this.el).remove();
        },
    });

    var EditItemView = Backbone.View.extend({
        tagName: "tr", 
        className: "edit-item", 
        template: _.template(['<td><label>見出し<input class="label" type="text" value="<%= label %>"/></label></td>', 
            '<td><label>内容<textarea class="content" type="text" max-width="100%" width="100%"><%= content %></textarea></label></td>',
            '<td><button type="button" class="update_button btn">更新</button></td>'
        ].join("\n")), 
        
        events: {
            "click .update_button": "updateOnEnter", 
        }, 

        updateOnEnter: function(e){
            var label = this.$(".label").val();
            var content = this.$(".content").val();
            this.yank(label,content);
        }, 

        yank: function(label,content){
            // todo: move it
            var target = this.$el.prev();
            this.model.set("label",label);
            this.model.set("content",content);
            this.model.trigger("redraw", target);
            this.remove();
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
            this.content_input = this.$("#content_input");
            this.notify_input = this.$("#notify_input");
            this._stored_data = null; //loaded data cached
            // model
            this.contentlist = new ItemList();
            this.contentlist.bind("add", this.addOne, this);
        }, 
        
        events: {
            "click #additem_button": "createItem",
            "click #reflesh_button": "refleshContent",
            "click #load_from_api_button": "loadDataFromAPI",
            "click #removeall_button": "removeAll"
        }, 
        
        addOne: function(item){
            var view = new ItemView({model: item});
            $(this.el).find("#contentlist").append($(view.render().el).data("view",view));
        }, 
        
        loadInitialData: function(params){
            if(!!params){
              this._stored_data = params;
            }
            return this.loadData(this._stored_data);
        },

        loadData: function(params){
            var contentlist = this.contentlist;
            _(params).each(function(param){
                contentlist.create(param);
            });

            $("#item-result tbody").sortable({
                delay: 150,
                helper: function(e, ui){
                    ui.children().each(function() {
                        $(this).width($(this).width());
                    });
                    return ui;
                }
            }).disableSelection();

        }, 

        removeAll: function(){
           $(this.el).find("#contentlist").empty();
        },

        refleshContent: function(){
           $(this.el).find("#contentlist").empty();
           this.loadData(this._stored_data);
        },

        loadDataFromAPI: function(ev){
           var self = this;
           var url = $(ev.currentTarget).attr("url");
           $.getJSON(url, {"page": get_page()}).done(function(data){
                $(self.el).find("#contentlist").empty();
                self.loadData(data); 
            });
        },

        collectData: function(){
            var get_text_or_val = function(e,expr){ 
              var e = e.find(expr);
              return e.text() || e.val();
            }
            return _($(this.el).find("#contentlist tr")).map(function(e){
                var e = $(e);
                return {
                    label: get_text_or_val(e, ".label"),
                    content: get_text_or_val(e, ".content"),
                    notify: !!e.find(".notify").attr("checked")
                };
            });
        }, 

        createItem: function(e){
            var label = this.label_input.val();
            var content = this.content_input.val();
            var notify = !!this.notify_input.attr("checked");
            if (!label || !content) return;

            this.contentlist.create({label: label, content: content, notify: notify});
            this.label_input.val("");
            this.content_input.val("");
        }, 
    });
</%text>
  var root =  $("#app");
  var appview = new AppView({el: root}); 
  root.data("appview", appview);
  appview.loadInitialData(${items|n}); <%doc> items is mako </%doc>
})();
</script>
