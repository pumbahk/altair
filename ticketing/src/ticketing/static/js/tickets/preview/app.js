// require backbone.js
// require altair/deferredqueue.js

/// models
var SVGStage = {"empty":0, "raw":1, "normalize":2}
var SVGStore = Backbone.Model.extend({
    defaults:{
        svg: null, 
        stage: SVGStage.empty
    }
});

var TemplateVarStore = Backbone.Model.extend({
    defaults: {
        vars: [], 
        values: {} // change to model, iff auto redrawing image after each change values of one.
    }
});

/// services
var DragAndDropSupportService = {
    compose: function(){
        var fns = arguments;
        return function(){
            var r;
            for (var i=0, j=fns.length; i<j; i++){
                r = fns[i].apply(this, arguments);
            }
            return r;
        }
  　},
    cancel: function(e){
        e.stopPropagation();
        e.preventDefault();
    },
    onDrop: function(file_use_fn){
      return function(e){
        var files = e.dataTransfer.files;
        for (var i=0, file; file=files[i]; i++){
          var reader = new FileReader();

          reader.onerror = function(e){ 
           alert('Error code: ' + e.target.error.code);
          }

          reader.onload = (function(aFile){
            return function(e){ //?
              file_use_fn(e);
            }
          })(file);
          reader.readAsText(file, "UTF-8");
        }
        return false;
      }
    },
}

var ConsoleMessage = { //use info, log, warn, error, dir
    success: console.debug, 
    error: console.debug, 
    info: console.debug, 
    warn: console.debug
}

/// viewmodels
var DropAreaViewModel = Backbone.View.extend({ //View?
    touched: function(){
        this.$el.addClass("touched");
    }, 
    untouched: function(){
        this.$el.removeClass("touched")
    }, 
});


/// views
var DragAndDropSVGSupportView = Backbone.View.extend({
  events: {
  }, 
  initialize: function(opts){
      this.message = opts.message || ConsoleMessage;
      this.vms = opts.vms || {};
      this.apis = opts.apis || {};
      var compose = DragAndDropSupportService.compose, 
          default_action_cancel = DragAndDropSupportService.cancel;

      this.el.addEventListener("dragenter", default_action_cancel, false);
      this.el.addEventListener('dragover',  compose(default_action_cancel, this.vms.drop_area.touched.bind(this.vms.drop_area)), false);
      this.el.addEventListener('dragleave', compose(default_action_cancel, this.vms.drop_area.untouched.bind(this.vms.drop_area)), false);
      this.el.addEventListener('drop',
                                compose(default_action_cancel,
                                        this.vms.drop_area.untouched.bind(this.vms.drop_area), 
                                        DragAndDropSupportService.onDrop(this.onLoadSVG.bind(this))),
                                false);
  }, 
  _onLoadSVGPassed: function(svg){
      var $loading = $("#loading_area");
      $loading.spinner("start");
      var self = this;

      return $.get(this.apis.normalize, {"svg": svg})
          .done(function(data){
              if(!data.status){
                  alert(data.message);
                  $loading.spinner("stop");
              }
              $.get(self.apis.previewbase64, {"svg": data.data})
                  .done(function(data){
                      if(!data.status){
                          $loading.spinner("stop"); 
                          return;
                      }
                      var $preview = $("#preview_area");
                      $preview.empty();
                      $preview.append($("<img title='preview' alt='preview todo upload file'>").attr("src", "data:image/png;base64,"+data.data));
                      $loading.spinner("stop");
                  })
                  .fail(function(s,err){
                      alert(s.responseText);
                      $loading.spinner("stop");
                  });
          })
          .fail(function(s,err){alert(s.responseText); $loading.spinner("stop");});
  }, 
  onLoadSVG: function(e){
      return this._onLoadSVGPassed(e.target.result)
  }
});

var NormalizeSVGCommunicationView = Backbone.View.extend({
});

var RenderingSVGCommunicationView = Backbone.View.extend({
});

var ManagementTemplateValuesView = Backbone.View.extend({
});
