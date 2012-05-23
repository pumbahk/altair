package util;

@:native("JSUtil.JSONParser")
extern class JSONParser {
    public static function decode(str:String):<Dynamic>;
    public static function encode(obj:Dynamic):String;
}