if (!window.app)
  window.app = {};

(function(app){
  "use strict";

  /// これはsubmitする前の状態での値。settingの範囲ではこちら
  var ticketSelectSourceModel = Object.create(
    {
      isEnough: function(){
        console.log("ok?"+(!!this.templateKind && !! this.previewType).toString());
        return !!this.templateKind && !! this.previewType;
      },
      sync: function(name, val){
        this[name] = val;
        console.log("sync: name={0} value={1}".replace("{0}",name).replace("{1}",val));
      }
    },
    {
      previewType: {value: null, writable: true},
      eventId: {value: null, writable: true},
      templateKind: {value: null, writable: true},
      templateId: {value: null, writable: true},
      createdTemplateId: {value: null, writable: true},
      isAfterCreatedFirst: {value: false, writable: true}
    });

  var selectContentTemplate = _.template('<% _.each(iterable, function(d){%><option value="<%= d.pk %>"><%= d.name %></option> <%});%>');
  var listingTicketTemplate = _.template([
    '<% _.each(tickets, function(d){%><li><a target="_blank" href="<%= d.url %>"><%= d.name %></a></li><%});%>'
  ].join("\n"));

  /// これはsubmitする際の状態
  var submitParamatersModel = Object.create(
    {
      sync: function(name, val){
        this[name] = val;
        console.log("sync: name={0} value={1}".replace("{0}",name).replace("{1}",val));
      },
      collect: function(){
        var r = {};
        _.each(this, function(v,k){
          if(typeof(k) !== "function"){
            r[k] = v;
          }
        });
        //r.fill_mapping = JSON.stringify(r.fill_mapping);
        return r;
      }
    },
    {
      name: {value: "", writable:true, enumerable:true},
      preview_type: {value: "default", writable:true, enumerable:true},
      template_kind: {value: "default", writable:true, enumerable:true},
      cover_print: {value: false, writable:true, enumerable:true},
      base_template_id: {value: null, writable:true, enumerable:true},
      drawing: {value: "", writable:true, enumerable:true},
      fill_mapping: {value: "{}", writable:true, enumerable:true},
    }
  );

  // Module needs: {"submit","setting","component"}
  var BrokerModule = {
    onTicketFormatSelectElementUpdate: function(html){
      this.submit.$el.find('select[name="ticket_format_id"]').html(html);
    },
    onTicketTemplateSelectElementUpdate: function(html){
      var $select = this.setting.$el.find('select[name="templates"]');
      $select.html(html);
      // hmm.
      h.synchronizedWait(function predicate(){return !!window.appView && $select.find("option").length >= 1;},
                         function then(){
                           $select.change();
                         });
    },
    onNewTicketsList: function(data){
      this.listing.onNewTicketsList(data);
    },
    onNewSVGData: function(data){
      //xxxx global variable: this variable create after loading component
      h.synchronizedWait(function predicate(){return !!window.appView;},
                         function then(){
                           window.appView.loadSVG(data.svg, data.preview_type);
                         });
    },
    onNewTicketFormatData: function(data){
      var self = this;
      h.synchronizedWait(function predicate(){return !!window.appView;},
                         function then(){
                           //xxxx global variable: this variable create after loading component
                           window.appView.views.params_view.reDrawTicketFormatCandidates(data.iterable, data.preview_type);
                           self.onTicketFormatSelectElementUpdate(selectContentTemplate({"iterable": data.iterable}));
                         });
    },
    onNewFillValues: function(data){
      var self = this;
      h.synchronizedWait(function predicate(){return !!window.appView;},
                         function then(){
                           //xxxx global variable: this variable create after loading component
                           window.appView.fillsVarsWithParams(data.params);
                         });
    },
    onAfterSubmitSuccess: function(data){
      this.models.source.sync("createdTemplateId", data.ticket_id);
      this.models.source.sync("isAfterCreatedFirst", true);
      this.choose.onChangeTemplateKindToEvent();
      this.userhandle.onClickHandleButton(this.submit.$el.parents(".userhandle").find(".js-next-btn"));
    },
    getCurrentSVG: function(){
      //xxxx global variable: this variable create after loading component
      return window.appView.getSVGData();
    },
    getCurrentVarsValues: function(){
      //xxxx global variable: this variable create after loading component
      return window.appView.getVarsValues();
    },
  };

  var SubmitAreaModule = {
    onChangeTicketName: function($el){
      this.broker.models.submit.sync("name", $el.val());
    },
    onChangeIsPrintConver: function($el){
      var v = $el.attr("checked") ? "y" : null;
      this.broker.models.submit.sync("cover_print", v);
    },

    collectParamatersForSubmit: function($form){
      var src = this.broker.models.source;

      var m = this.broker.models.submit;
      m.preview_type = src.previewType;
      m.template_kind = src.templateKind;
      m.drawing = this.broker.getCurrentSVG();
      m.fill_mapping = JSON.stringify(this.broker.getCurrentVarsValues());
      return this.broker.models.submit.collect();
    },
    onSubmitCreate: function($form){
      var url = $form.attr("action");
      var params = this.collectParamatersForSubmit($form);
      params.create = true;
      return $.post(url, params)
        .fail(
          function(){ this.$el.text("error: url="+url);}.bind(this)
        ).done(
          function(data){
            this.broker.onAfterSubmitSuccess(data);
          }.bind(this)
        );
    },
    onSubmitUpdate: function($form){
      var url = $form.attr("action");
      var params = this.collectParamatersForSubmit($form);
      params.update = true;
      return $.post(url, params)
        .fail(
          function(){ this.$el.text("error: url="+url);}.bind(this)
        ).done(
          function(data){
            this.broker.onAfterSubmitSuccess(data);
          }.bind(this)
        );
   }
  };

  var SettingAreaModule = {
    onChangeTicketTemplate: function($el){
      this.broker.models.source.sync("templateId", $el.val());
      this.broker.models.submit.sync("base_template_id", $el.val());
      return this.broker.component.onChangeTicketTemplate($el);
    },
    onClickStickyButton: function($el){
      if($el.hasClass("sticky")){
        $el.removeClass("sticky");
        $el.css({"position": "static"});
      }else {
        $el.addClass("sticky");
        $el.css({"position": "fixed"});
      }
    },
    onClickFillButton: function($el){
      return this.broker.component.onFillValues($el);
    },
    bindClipboardCopy: function($el, moviePath){
      ZeroClipboard.config({"moviePath": moviePath});
      $el.find('.copy-button').each(function(i,el){new ZeroClipboard(el);});
    },
    bindHelpPopOver: function($el){
      $el.find('[rel=popover]').popover();
    }
  };

  var ChooseAreaModule = {
    onChangePreviewType: function($el){
      var m = this.broker.models.source;
      m.sync("previewType",$el.val());
      if(m.isEnough()){
        return this.broker.component.onChangePreviewType($el);
      }
    },
    onChangeTemplateKind: function($el){
      var m = this.broker.models.source;
      m.sync("eventId", $el.val());
      m.sync("templateKind", (!!$el.val()) ? "event" : "base");
      if(m.isEnough()){
        return this.broker.component.onChangePreviewType($el); //xxx:
      }
    },
    onChangeTemplateKindToEvent: function(){
      var $select = this.$el.find('input[name="event_id"]');
      var e = _.find($select, function(e){ return !!$(e).val();});  //xxx:
      $(e).attr("checked","checked");
      return this.onChangeTemplateKind($(e));
    }
  };

  var ListingAreaModule = {
    onNewTicketsList: function(data){
      var $wrapper = this.$el.find("ul#listing-ticket");
      var html = listingTicketTemplate({"tickets": data.tickets});
      $wrapper.html(html);
    }
  };

  // Module needs {$el, broker,loadcomponent_url, gettingsvg_url, gettingformat_url, gettingtemplate_url, select_template"}
  var ComponentAreaModule = {
    onChangePreviewType: function($el){
      var val = this.broker.models.source.previewType;
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
      var params={"event_id": this.broker.models.source.eventId};
      if (this.broker.models.source.isAfterCreatedFirst){
        this.broker.models.source.sync("isAfterCreatedFirst",false);
        params.template_id = this.broker.models.source.createdTemplateId;
      }
      return $.post(url, params).fail(
        function(){ this.$el.text("error: url="+url);}.bind(this)
      ).done(
        function(data){ 
          this.broker.onTicketTemplateSelectElementUpdate(selectContentTemplate({"iterable": data.iterable}));
          this.broker.onNewTicketsList(data);
        }.bind(this)
      );
    },
    onChangeTicketTemplate: function($el){
      var val = $el.val();
      var previewType =  this.broker.models.source.previewType;
      if(!!previewType){
        var url = this.gettingsvg_url.replace("__ticket_id", val).replace("__previewtype", previewType);
        return this.sendingSVGViaRequest(url);
      }
    },
    sendingSVGViaRequest: function(url){
      return $.get(url).fail(
        function(){ this.$el.text("error: url="+url);}.bind(this)
      ).done(
        function(data){this.broker.onNewSVGData(data);}.bind(this)
      );
    },
    onFillValues: function($el){
      var previewType = this.broker.models.source.previewType;
      var templateId =  this.broker.models.source.templateId;
      if(!!templateId && !!previewType){
        var url = this.gettingvarsvals_url.replace("__ticket_id", templateId).replace("__previewtype", previewType);
        return this.loadingFillVallues(url);
      }
    },
    loadingFillVallues: function(url){
      return $.get(url).fail(
        function(){ this.$el.text("error: url="+url);}.bind(this)
      ).done(
        function(data){this.broker.onNewFillValues(data);}.bind(this)
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

  app.ticketSelectSourceModel = ticketSelectSourceModel;
  app.submitParamatersModel = submitParamatersModel;

  app.UserHandleAreaModule = UserHandleAreaModule;
  app.ChooseAreaModule = ChooseAreaModule;
  app.ComponentAreaModule = ComponentAreaModule;
  app.SettingAreaModule = SettingAreaModule;
  app.SubmitAreaModule = SubmitAreaModule;
  app.ListingAreaModule = ListingAreaModule;
  app.BrokerModule = BrokerModule;
})(window.app);

