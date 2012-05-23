package util;

import util.json.JSON;

class JSONLoader {

    var cb:JSONLoaderCallback;

    public function new(cb:JSONLoaderCallback)
    {
        this.cb = cb;
    }

    public function load(url:String, flag:Int)
    {
        var r = new haxe.Http(url);
        r.onError = function(msg:String) { this.onError(msg, flag); };
        r.onData  = function(msg:String) { this.onSuccess(msg, flag); };
        r.request(false);
    }

    private function onError(msg:String, flag:Int):Void
    {
        this.cb.onError(msg, flag);
    }

    private function onSuccess(msg:String, flag:Int):Void
    {
       var obj:Dynamic = JSON.decode(msg);
       this.cb.onSuccess(obj, flag);
    }
}