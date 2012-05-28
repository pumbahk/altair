package views.rendering.js.dom;
import js.JQuery;
import js.JQuery.JqEvent;

class BoundingBoxRenderer extends JSDOMComponentRenderer {
    var imageUrl:String;
    var position:Point;
    var size:Point;

    static function __init__() {
        Spi.rendererRegistry.addImplementation(BoundingBox, BoundingBoxRenderer);
    }

    public override function setup():JQuery {
        return new JQuery('<div class="component-bounding_box"></div>');
    }

    public override function realize(component:Dynamic):Void {
        imageUrl = component.imageUrl;
        position = component.position;
        size = component.size;
        view_.scheduleRefresh(this);
    }

    public override function refresh():Void {
        var position = view_.inchToPixelP(this.position);
        var size = view_.inchToPixelP(this.size);

        size.x -= Utils.toPixel(Utils.getComputedStyle(this.n[0], 'border-left-width'))
                + Utils.toPixel(Utils.getComputedStyle(this.n[0], 'border-right-width'));
        size.y -= Utils.toPixel(Utils.getComputedStyle(this.n[0], 'border-top-width'))
                + Utils.toPixel(Utils.getComputedStyle(this.n[0], 'border-bottom-width'));

        untyped __js__("this.n.css")(
            { left: Std.string(position.x) + "px",
              top: Std.string(position.y) + "px",
              width: Std.string(size.x) + "px",
              height: Std.string(size.y) + "px" });
        if (imageUrl != null) {
            untyped __js__("this.n.css")(
                { backgroundImage: "url(" + imageUrl + ")",
                  backgroundPosition: "-1 -1",
                  backgroundRepeat: "none",
                  backgroundSize: "contain" });
        } else {
            untyped __js__("this.n.css")(
                { backgroundImage: "",
                  backgroundPosition: "",
                  backgroundRepeat: "",
                  backgroundSize: "" });
        }
        super.refresh();
    }
}

