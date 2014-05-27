if (!window.app)
  window.app = {};

(function(app){
  "use strict";
  var selectContentTemplate = _.template('<% _.each(iterable, function(d){%><option value="<%= d.pk %>"><%= d.name %></option> <%});%>');

  // Module needs: {"submit","setting","component"}
  var BrokerModule = {
    onTicketFormatSelectElementUpdate: function(html){
      this.submit.$el.find('select[name="ticket_format_id"]').html(html);
    },
    onTicketTemplateSelectElementUpdate: function(html){
      this.setting.$el.find('select[name="templates"]').html(html);
    },
    onNewSVGData: function(data){
      //xxxx global variable: this variable create after loading component
      h.synchronizedWait(function predicate(){return !!window.appView},
                         function then(){
                           window.appView.loadSVG(data.svg, data.preview_type);
                         });
    },
    onNewTicketFormatData: function(data){
      var self = this;
      h.synchronizedWait(function predicate(){return !!window.appView},
                         function then(){
                           //xxxx global variable: this variable create after loading component
                           window.appView.views.params_view.reDrawTicketFormatCandidates(data.iterable, data.preview_type);
                           self.onTicketFormatSelectElementUpdate(selectContentTemplate({"iterable": data.iterable}));
                         });
    },
    getCurrentSVG: function(){
      //xxxx global variable: this variable create after loading component
      return window.appView.models.svg.get("data");
    }
  };
  
  var SubmitAreaModule = {
    onSubmit: function($form){
      var svg = this.broker.getCurrentSVG()
      this.$el.find('input[name="drawing"]').val(svg);
      var params = h.serialize($form);
      var url = $form.attr("action");
      return $.post(url, params)
      .fail(
        function(){ this.$el.text("error: url="+url);}.bind(this)
      ).done(
        function(data){ this.$el.text(data); }.bind(this)
      );
    }
  };

  var SettingAreaModule = {
    onChangePreviewType: function($el){
      return this.broker.component.onChangePreviewType($el);
    },
    onChangeTicketTemplate: function($el){
      return this.broker.component.onChangeTicketTemplate($el);
    }
  };

  // Module needs {$el, broker,loadcomponent_url, gettingsvg_url, gettingformat_url, gettingtemplate_url, select_template"}
  var ComponentAreaModule = {
    onChangePreviewType: function($el){
      var val = $el.val();
      this.preview_type = val;
      var load_url = this.loadcomponent_url.replace("__previewtype", val);
      var template_url = this.gettingtemplate_url.replace("__previewtype", val);
      var format_url = this.gettingformat_url.replace("__previewtype", val);
      return this.gettingNewTemplates(template_url)
        .then(function(){return this.loadingComponent(load_url);}.bind(this))
        .then(function(){return this.gettingNewFormats(format_url);}.bind(this));
    },
    loadingComponent: function(url){
      if(!!window.appView){
        // if loaded already,then skip;
        var $dfd = new $.Deferred();
        $dfd.resolve();
        return $dfd.promise();
      }
      return $.get(url).fail(
        function(){ this.$el.text("error: url="+url);}.bind(this)
      ).done(
        function(html){ this.$el.html(html); }.bind(this)
      );
    },
    gettingNewFormats: function(url){
      var self = this;
      return $.get(url).fail(
        function(){ this.$el.text("error: url="+url);}.bind(this)
      ).done(
        function(data){
          self.ticket_formats_iterable = data.iterable;
          self.broker.onNewTicketFormatData(data);
        });
    },
    gettingNewTemplates: function(url){
      return $.get(url).fail(
        function(){ this.$el.text("error: url="+url);}.bind(this)
      ).done(
        function(data){ 
          this.broker.onTicketTemplateSelectElementUpdate(selectContentTemplate({"iterable": data.iterable}));
        }.bind(this)
      );
    },
    onChangeTicketTemplate: function($el){
      var val = $el.val();
      var url = this.gettingsvg_url.replace("__ticket_id", val).replace("__previewtype", this.preview_type);

      return this.sendingSVGViaRequest(url);
    },
    sendingSVGViaRequest: function(url){
      return $.get(url).fail(
        function(){ this.$el.text("error: url="+url);}.bind(this)
      ).done(
        function(data){this.broker.onNewSVGData(data);}.bind(this)
      );
    }
  };

  var UserHandleAreaModule = {
    onClickNavigation: function($el){
      var $prevel = this.$el.find("a.current");
      var nextUserHandleId = $el.data("toggle").substring(1,$el.data("toggle").length); //lstrip #
      if($prevel.data("toggle") != nextUserHandleId){
        $prevel.find(".badge").removeClass("badge-inverse");
        $prevel.removeClass("current");

        _.each(this.$el.find(".userhandle"), function(e){
          var $e = $(e);
          if($e.attr("id") == nextUserHandleId){
            $e.show();
          }else {
            $e.hide();
          }
        });
        $el.find(".badge").addClass("badge-inverse");
        $el.addClass("current");
      }
    },
    onClickHandleButton: function($el){
      $($el.data("toggle")).click();
    }
  };
  app.UserHandleAreaModule = UserHandleAreaModule;
  app.ComponentAreaModule = ComponentAreaModule;
  app.SettingAreaModule = SettingAreaModule;
  app.SubmitAreaModule = SubmitAreaModule;
  app.BrokerModule = BrokerModule;
})(window.app);

