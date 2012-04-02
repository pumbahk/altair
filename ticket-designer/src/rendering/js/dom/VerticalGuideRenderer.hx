package rendering.js.dom;
import js.JQuery;
import js.JQuery.JqEvent;

class VerticalGuideRenderer extends JSDOMComponentRenderer {
    var offset:Float;

    static function __init__() {
        Spi.rendererRegistry.addImplementation(VerticalGuide, VerticalGuideRenderer);
    }

    public override function setup():JQuery {
        super.setup();
        return new JQuery('<div class="component-vertical_guide"></div>');
    }

    public override function realize(component:Dynamic):Void {
        offset = component.position.x;
        view_.scheduleRefresh(this);
    }

    public override function refresh():Void {
        untyped __js__("this.n.css")(
            { left: Std.string(view_.inchToPixel(offset)) + "px",
              top: "0px",
              width: "0px",
              height: "100%",
              borderWidth: "1px" });
        super.refresh();
    }
}
