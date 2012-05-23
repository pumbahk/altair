package util;

interface JSONLoaderCallback {
    public function onSuccess(obj:Dynamic, flag:Int):Void;
    public function onError(reason:String, flag:Int):Void;
}