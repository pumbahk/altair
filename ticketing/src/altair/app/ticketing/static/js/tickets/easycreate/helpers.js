if(!window.h)
	window.h = {};

(function(h){
  // _.object
  h.object = function object(list, values) {
    if (list === null) return {};
    var result = {};
    for (var i = 0, length = list.length; i < length; i++) {
      if (values) {
        result[list[i]] = values[i];
      } else {
        result[list[i][0]] = list[i][1];
      }
    }
    return result;
  };

  h.serialize = function serialize($form){
    var xs = _.map($form.find("select,input"), function(e){
      var $e = $(e);
      if($e.attr("type") == "checkbox"){
        return $e.attr("checked") ? [$e.attr("name"),"y"] : null;
      } else if($e.attr("type") == "radio"){
        return $e.attr("checked") ? [$e.attr("name"), $e.val()] : null;
      } else {
        return [$e.attr("name"),$e.val()];
      }
    });
    return h.object(_.compact(xs));
  };

  defaultWaitTimes = [50, 100, 300, 750, 1500, 3000, 7000, 160000];
  h.synchronizedWait = function synchronizedWait(prediate, onSuccess, waitTimes){
    if(!waitTimes){
      waitTimes = Array.apply(null,defaultWaitTimes);
    }
    setTimeout((function looping(){
      if(prediate()){
        onSuccess();
      }else{
        var sec = waitTimes.shift();
        if(!!sec){
          setTimeout(looping,sec);
        }
      }
    }));
  };
})(window.h);
