package views.rendering.js.dom;
import js.JQuery;
import js.JQuery.JqEvent;

class RubberBandRenderer extends JSDOMComponentRenderer {
    var text:String;
    var position:Point;
    var size:Point;

    static function __init__() {
        Spi.rendererRegistry.addImplementation(RubberBand, RubberBandRenderer);
    }

    public override function setup():JQuery {
        return new JQuery('<div class="component-rubber_band"></div>');
    }

    public override function realize(component:Dynamic):Void {
        position = component.position;
        size = component.size;
        view_.scheduleRefresh(this);
    }

    public override function refresh():Void {
        var position = view_.inchToPixelP(this.position);
        var size = view_.inchToPixelP(this.size);
        untyped __js__("this.n.css")(
            { left: Std.string(position.x) + "px",
              top: Std.string(position.y) + "px",
              width: Std.string(size.x) + "px",
              height: Std.string(size.y) + "px" });
        super.refresh();
    }
}
