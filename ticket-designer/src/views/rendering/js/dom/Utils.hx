package views.rendering.js.dom;
import views.rendering.js.Html5Dom;
import js.Dom;
import js.Lib;

class Utils {
    public static function toPixel(str:String):Float {
        if (str == '')
            return 0.;
        var regex = ~/(-?(?:[0-9]+(?:\.[0-9]+)?|\.[0-9]+)(?:[eE][-+]?[0-9]+)?)(.*)/;
        if (!regex.match(str))
            throw new IllegalArgumentException("Malformed value: " + str);
        var unit = regex.matched(2) == '' ? 'px': regex.matched(2);
        if (unit != 'px')
            throw new UnsupportedException("Unsupported unit: " + regex.matched(2));
        return Std.parseFloat(regex.matched(1));
    }

    public static function getComputedStyle(n:HtmlDom, key:String):String {
        var retval = {};
        var getComputedStyle:Dom->String->CSSStyleDeclaration = cast (cast Lib.window).getComputedStyle;
        var currentStyle:Style = untyped __js__('n.currentStyle');
        if (getComputedStyle != null) {
            return getComputedStyle(cast n, null).getPropertyValue(~/(?!^)[A-Z]/.customReplace(key, function (r:EReg) { return "-" + r.matched(0).toLowerCase(); }));
        } else if (currentStyle != null) {
            return Reflect.field(currentStyle, key);
        }
        return Reflect.field(n.style, key);
    }
}
