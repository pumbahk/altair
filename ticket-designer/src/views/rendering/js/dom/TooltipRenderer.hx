package views.rendering.js.dom;
import js.JQuery;
import js.JQuery.JqEvent;

class TooltipRenderer extends JSDOMRenderer {
    var text:String;
    var position:Point;
    var fontSize:Float;
    var selected:Bool;

    static function __init__() {
        Spi.rendererRegistry.addImplementation(Tooltip, TooltipRenderer);
    }

    public override function setup():JQuery {
        return new JQuery('<div class="component-tooltip"></div>');
    }

    public override function realize(component:Dynamic):Void {
        text = component.text;
        position = component.position;
        fontSize = component.fontSize;
        view_.scheduleRefresh(this);
    }

    public override function refresh():Void {
        untyped __js__("this.n.css")(
            { left: Std.string(position.x) + "px",
              top: Std.string(position.y) + "px",
              fontSize: fontSize + "px" });
        n.text(text);
        super.refresh();
    }
}
