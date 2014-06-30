if (!window.app)
  window.app = {};

(function(app){
  "use strict";

  /// これはsubmitする前の状態での値。settingの範囲ではこちら
  var ticketSelectSourceModel = Object.create(
    {
      isEnough: function(){
        // console.log("ok?"+(!!this.templateKind && !! this.previewType).toString());
        return !!this.templateKind && !! this.previewType;
      },
      sync: function(name, val){
        this[name] = val;
        // console.log("sync: name={0} value={1}".replace("{0}",name).replace("{1}",val));
      }
    },
    {
      previewType: {value: null, writable: true},
      eventId: {value: null, writable: true},
      templateKind: {value: null, writable: true},
      templateId: {value: null, writable: true},
      createdTemplateId: {value: null, writable: true},
      isAfterCreatedFirst: {value: false, writable: true},
      callback: {value: null, writable: true}
    });

  var selectContentTemplate = _.template('<% _.each(iterable, function(d){%><option value="<%= d.pk %>"><%= d.name %></option> <%});%>');
  var listingTicketTemplate = _.template([
    '<% _.each(tickets, function(d){%><li><input name="mapping_id" type="radio" value="<%= d.pk %>"></input><a target="_blank" href="<%= d.url %>"><%= d.name %></a></li><%});%>'
  ].join("\n"));

  /// これはsubmitする際の状態
  var submitParamatersModel = Object.create(
    {
      sync: function(name, val){
        this[name] = val;
        // console.log("sync: name={0} value={1}".replace("{0}",name).replace("{1}",val));
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

  // これはtranscribeする際の状態
  var transcribeParamatersModel = Object.create(
    {
      sync: function(name, val){
        this[name] = val;
        // console.log("sync: name={0} value={1}".replace("{0}",name).replace("{1}",val));
      },
      collect: function(){
        var r = {};
        _.each(this, function(v,k){
          if(typeof(k) !== "function"){
            r[k] = v;
          }
        });
        return r;
      }
    },
    {
      name: {value: "", writable:true, enumerable:true},
      base_template_id: {value: null, writable:true, enumerable:true},
      mapping_id: {value: "{}", writable:true, enumerable:true},
    }
  );

  
  // Module needs: {"submit","setting","component"}
  var BrokerModule = {
    onChangeToEventTicket: function(){
      this.setting.receiveChangeToEventTicketLabel();
      this.submit.receiveChangeToEventTicket();
    },
    onChangeToTicketTemplate: function(){
      this.setting.receiveChangeToTicketTemplateLabel();
      this.submit.receiveChangeToTicketTemplate();
    },
    onChangeTicketTemplate: function($el){
      var text = $el.find("option:selected").text();
      this.submit.receiveDefaultTicketName(text);
      this.listing.receiveChangeSelectedMapping(text, $el.val());
      return this.component.receiveSVGRequest($el.val());
    },
    onTicketFormatSelectElementUpdate: function(html){
      this.submit.$el.find('select[name="ticket_format_id"]').html(html);
    },
    onTicketTemplateSelectElementUpdate: function(html){
      var $select = this.setting.$el.find('select[name="templates"]');
      var mo = new MutationObserver(function(mrList,mo){
        // console.log("template select changed");
        $select.change();
        mo.disconnect();
      });
      mo.observe($select[0], {childList: true});
      $select.html(html);
    },
    onNewTicketsList: function(data){
      this.listing.receiveNewTicketsList(data);
    },
    onNewSVGData: function(data){
      var self = this;
      //xxxx global variable: this variable create after loading component
      h.synchronizedWait(function predicate(){return !!window.appView;},
                         function then(){
                           var srcModel = app.broker.models.source;
                           var cancelFirstPreview = (srcModel.templateKind === "event");
                           window.appView.loadSVG(data.svg, data.preview_type, cancelFirstPreview);
                           // for fillvaluse input ui (that is table object so checking target.nodeName === "TBODY"'s chlid).
                           var mo = new MutationObserver(function(mrList,mo){
                             //console.dir(mrList);
                             var firstRow = _.find(mrList, function(mr){return mr.target.nodeName === "TBODY";});
                             if(!!firstRow){
                               mo.disconnect();
                               if(!!srcModel.eventId && !!srcModel.templateId){
                                 // console.log("ok;")
                                 app.component.onFillValues(null);
                               }
                             }
                           });
                           mo.observe(self.component.$el[0], {childList: true, subtree: true});
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
      // console.log("on new fill values");
      h.synchronizedWait(function predicate(){return !!window.appView;},
                         function then(){
                           //xxxx global variable: this variable create after loading component
                           window.appView.fillsVarsWithParams(data.params);
                           window.appView.reDrawImage();
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
    receiveDefaultTicketName: function(name){
      this.$el.find('input[name="name"]').val(name);
      this.broker.models.submit.sync("name", name);
    },
    onChangeTicketName: function($el){
      this.broker.models.submit.sync("name", $el.val());
    },
    onChangeIsPrintConver: function($el){
      var v = $el.attr("checked") ? "y" : null;
      this.broker.models.submit.sync("cover_print", v);
    },
    receiveChangeToEventTicket: function(){
      this.$el.find('input[name="update"]').show();
    },
    receiveChangeToTicketTemplate: function(){
      this.$el.find('input[name="update"]').hide();
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
          function(){ this.broker.message.errorMessage("error: url="+url);}.bind(this)
        ).done(
          function(data){
            this.broker.message.successMessage("チケット券面を１つ作成しました");
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
          function(){ this.broker.message.errorMessage("error: url="+url);}.bind(this)
        ).done(
          function(data){
            this.broker.message.successMessage("チケット券面を１つ更新しました");
            this.broker.onAfterSubmitSuccess(data);
          }.bind(this)
        );
   }
  };

  var SettingAreaModule = {
    receiveChangeToEventTicketLabel: function(){
      this.$el.find("#templates").parents(".control-group").find("label").text("チケット券面");
    },
    receiveChangeToTicketTemplateLabel: function(){
      this.$el.find("#templates").parents(".control-group").find("label").text("券面テンプレート");
    },
    onChangeTicketTemplate: function($el){
      this.broker.models.source.sync("templateId", $el.val());
      this.broker.models.submit.sync("base_template_id", $el.val());
      return this.broker.onChangeTicketTemplate($el);
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
    bindClipboardCopy: function($el, moviePath){
      ZeroClipboard.config({"moviePath": moviePath});
      $el.find('.copy-button').each(function(i,el){
        var zc = new ZeroClipboard(el);
        zc.on("complete", function(_){
          var $wrapper = $(el).parents(".label").eq(0);
          $wrapper.addClass("label-warning");
          setTimeout(function(){$wrapper.removeClass("label-warning");}, 500);
        });
      });
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
      var templateKind = (!!$el.val()) ? "event" : "base";
      m.sync("templateKind", templateKind);

      if(templateKind === "event"){
        this.broker.onChangeToEventTicket();
      }else {
        this.broker.onChangeToTicketTemplate();
      }
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
    receiveNewTicketsList: function(data){
      var $wrapper;
      if(this.broker.models.source.templateKind === "event"){
          $wrapper = this.$el.find("ul#listing-ticket");
      }else {
          $wrapper = this.$el.find("ul#listing-template");
      }
      var html = listingTicketTemplate({"tickets": data.tickets});
      $wrapper.html(html);
    },
    receiveChangeSelectedTemplate: function(name){
      this.$el.find(".selected-template").text(name);
    },
    receiveChangeSelectedMapping: function(name, templateId){
      this.broker.models.transcribe.sync("name", name);
      this.broker.models.transcribe.sync("mapping_id", templateId);
      this.$el.find(".selected-mapping").text(name);
    },
    onChangeSelectTemplate: function($el){
      var text = $el.parent("li").find("a").text();
      this.broker.models.transcribe.sync("base_template_id",$el.val());
      this.receiveChangeSelectedTemplate(text);
    },
    onChangeTicketName: function($el){
      this.broker.models.transcribe.sync("name", $el.val());
    },
    onSubmitTranscribe: function($form){
      var url = $form.attr("action");
      var params = this.broker.models.transcribe.collect();
      return $.post(url, params)
        .fail(
          function(){ this.broker.message.errorMessage("error: url="+url);}.bind(this)
        ).done(
          function(data){
            this.broker.message.successMessage("チケット券面を１つ転写しました");
            this.broker.onAfterSubmitSuccess(data);
          }.bind(this)
        );
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
        function(){ this.broker.message.errorMessage("error: url="+url);}.bind(this)
      ).done(
        function(html){ this.$el.html(html); }.bind(this)
      );
    },
    gettingNewFormats: function(url){
      var self = this;
      return $.get(url).fail(
        function(){ this.broker.message.errorMessage("error: url="+url);}.bind(this)
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
        function(){ this.broker.message.errorMessage("error: url="+url);}.bind(this)
      ).done(
        function(data){ 
          this.broker.onTicketTemplateSelectElementUpdate(selectContentTemplate({"iterable": data.iterable}));
          this.broker.onNewTicketsList(data);
        }.bind(this)
      );
    },
    receiveSVGRequest: function(ticketId){
      var val = ticketId;
      var previewType =  this.broker.models.source.previewType;
      if(!!previewType){
        var url = this.gettingsvg_url.replace("__ticket_id", val).replace("__previewtype", previewType);
        return this.sendingSVGViaRequest(url);
      }
    },
    sendingSVGViaRequest: function(url){
      return $.get(url).fail(
        function(){ this.broker.message.errorMessage("error: url="+url);}.bind(this)
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
        function(){ this.broker.message.errorMessage("error: url="+url);}.bind(this)
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

  var MessageServiceModule = {
    doMessage: function(name, expr, message){
      var messages = this.$el.find(".message");
      messages.hide();
      var target = this.$el.find(".message"+expr);
      if (target.length <= 0){
        var idname = expr.substring(1,expr.length);
        target = $('<div class="alert message">');
        target.attr('id', idname).addClass("alert-"+name);  //xx
        this.$el.append(target);
      }
      target.text(message);
      target.show();
    },
    successMessage: function(message){
      this.doMessage("success",this.success, message);
    },
    infoMessage: function(message){
      this.doMessage("info", this.info, message);
    },
    alertMessage: function(message){
      this.doMessage("alert", this.alert, message);
    },
    errorMessage: function(message){
      this.doMessage("error", this.error, message);
    }
  };

  app.MessageServiceModule = MessageServiceModule;

  app.ticketSelectSourceModel = ticketSelectSourceModel;
  app.submitParamatersModel = submitParamatersModel;
  app.transcribeParamatersModel = transcribeParamatersModel;

  app.UserHandleAreaModule = UserHandleAreaModule;
  app.ChooseAreaModule = ChooseAreaModule;
  app.ComponentAreaModule = ComponentAreaModule;
  app.SettingAreaModule = SettingAreaModule;
  app.SubmitAreaModule = SubmitAreaModule;
  app.ListingAreaModule = ListingAreaModule;
  app.BrokerModule = BrokerModule;
})(window.app);

