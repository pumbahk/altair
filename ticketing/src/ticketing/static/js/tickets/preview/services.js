if (!window.preview)
    window.preview = {}

preview.DragAndDropSupportService = {
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
           console.warn('Error code: ' + e.target.error.code);
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
