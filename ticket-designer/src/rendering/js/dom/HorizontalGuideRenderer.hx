package rendering.js.dom;
import js.JQuery;
import js.JQuery.JqEvent;

class HorizontalGuideRenderer extends JSDOMComponentRenderer {
    var offset:Float;

    static function __init__() {
        Spi.rendererFactory.addImplementation(HorizontalGuide, HorizontalGuideRenderer);
    }

    public override function setup():JQuery {
        return new JQuery('<div class="component-horizontal_guide"></div>');
    }

    public override function realize(component:Dynamic):Void {
        component = cast(component, HorizontalGuide);
        offset = component.position.y;
        view_.scheduleRefresh(this);
    }

    public override function refresh():Void {
        untyped __js__("this.n.css")(
            { left: "0px",
              top: Std.string(view_.inchToPixel(offset)) + "px",
              width: "100%",
              height: "0px",
              borderWidth: "1px" });
        super.refresh();
    }
}
