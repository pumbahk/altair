package views.rendering.js.dom;
import js.JQuery;
import js.JQuery.JqEvent;

class TextComponentRenderer extends JSDOMComponentRenderer {
    var text:String;
    var position:Point;
    var size:Point;
    var fontSize:Float;
    var selected:Bool;

    static function __init__() {
        Spi.rendererRegistry.addImplementation(TextComponent, TextComponentRenderer);
    }

    public override function setup():JQuery {
        return new JQuery('<div class="component-text"></div>');
    }

    public override function realize(component:Dynamic):Void {
        text = component.text;
        position = component.position;
        fontSize = component.fontSize;
        size = component.size;
        selected = component.selected;
        view_.scheduleRefresh(this);
    }

    public override function refresh():Void {
        var position = view_.inchToPixelP(this.position);
        var size = view_.inchToPixelP(this.size);
        if (selected)
            this.n.addClass("selected");
        else
            this.n.removeClass("selected");
        untyped __js__("this.n.css")(
            { left: Std.string(position.x) + "px",
              top: Std.string(position.y) + "px",
              fontSize: Std.string(
                view_.inchToPixel(UnitUtils.pointToInch(fontSize))) + "px",
              width: Std.string(size.x) + "px",
              height: Std.string(size.y) + "px" });
        n.text(text);
        super.refresh();
    }
}
