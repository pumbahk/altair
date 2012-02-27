package rendering.js.dom;
import js.JQuery;
import js.JQuery.JqEvent;

class TextComponentRenderer extends JSDOMComponentRenderer {
    var text:String;
    var position:Point;
    var fontSize:Float;

    static function __init__() {
        Spi.rendererFactory.addImplementation(TextComponent, TextComponentRenderer);
    }

    public override function setup():JQuery {
        return new JQuery('<div class="component-text"></div>');
    }

    public override function realize(component:Dynamic):Void {
        component = cast(component, TextComponent);
        text = component.text;
        position = component.position;
        fontSize = component.fontSize;
        view_.scheduleRefresh(this);
    }

    public override function refresh():Void {
        var pos = view_.inchToPixelP(position);
        untyped __js__("this.n.css")(
            { left: Std.string(pos.x) + "px",
              top: Std.string(pos.y) + "px",
              fontSize: Std.string(
                view_.inchToPixel(UnitUtils.pointToInch(fontSize))) + "px" });
        n.text(text);
        super.refresh();
    }
}
