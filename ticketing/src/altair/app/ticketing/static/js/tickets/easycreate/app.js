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
      window.appView.loadSVG(data.svg, data.preview_type);
    },
    onNewTicketFormatData: function(data){
      var self = this;
      var wait_times = [50, 100, 300, 750, 1500, 3000, 7000, 160000];
      setTimeout((function looping(){
        //xxxx global variable: this variable create after loading component
        if(!!window.appView){
          window.appView.views.params_view.reDrawTicketFormatCandidates(data.iterable, data.preview_type);
          self.onTicketFormatSelectElementUpdate(selectContentTemplate({"iterable": data.iterable}));
        } else {
          var sec = wait_times.shift();
          !!sec && setTimeout(looping, sec);
        }
      }), wait_times.shift());
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
      return $.post($form.attr("action"), params)
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

  app.ComponentAreaModule = ComponentAreaModule;
  app.SettingAreaModule = SettingAreaModule;
  app.SubmitAreaModule = SubmitAreaModule;
  app.BrokerModule = BrokerModule;
})(window.app);
