package views.rendering.js.dom;
import js.JQuery;
import js.JQuery.JqEvent;
import js.Lib;
import views.rendering.js.Html5Dom.Window;
import views.rendering.js.Html5Dom.HTMLCanvasElement;
import views.rendering.js.Html5Dom.CanvasRenderingContext2D;
import Utils;

class ImageComponentRenderer extends JSDOMComponentRenderer {
    var imageUrl:String;
    var position:Point;
    var size:Point;
    var selected:Bool;
    var preferredUnit:UnitKind;

    var canvasNode:HTMLCanvasElement;
    var textNode:JQuery;

    static function __init__() {
        Spi.rendererRegistry.addImplementation(ImageComponent, ImageComponentRenderer);
    }

    public override function setup():JQuery {
        var n = new JQuery('<div class="component-image"><canvas></canvas><div class="text"></div></div>');
        canvasNode = cast n.find("canvas")[0];
        textNode = n.find(".text");
        return n;
    }

    public override function realize(component:Dynamic):Void {
        imageUrl = component.imageUrl;
        position = component.position;
        size = component.size;
        selected = component.selected;
        preferredUnit = component.preferredUnit;
        view_.scheduleRefresh(this);
    }

    public override function refresh():Void {
        var position = view_.inchToPixelP(this.position);
        var size = view_.inchToPixelP(this.size);
        if (selected)
            this.n.addClass("selected");
        else
            this.n.removeClass("selected");

        position.x -= views.rendering.js.dom.Utils.toPixel(cast views.rendering.js.dom.Utils.getComputedStyle(this.n[0], 'borderLeftWidth'))
                      + views.rendering.js.dom.Utils.toPixel(cast views.rendering.js.dom.Utils.getComputedStyle(this.n[0], 'marginLeft')) + 1;
        position.y -= views.rendering.js.dom.Utils.toPixel(cast views.rendering.js.dom.Utils.getComputedStyle(this.n[0], 'borderTopWidth'))
                      + views.rendering.js.dom.Utils.toPixel(cast views.rendering.js.dom.Utils.getComputedStyle(this.n[0], 'marginTop')) + 1;

        canvasNode.width = Std.int(size.x);
        canvasNode.height = Std.int(size.y);
        var ctx = canvasNode.getContext("2d");
        ctx.strokeStyle = "#ddd";
        ctx.fillStyle = "#fff";
        ctx.fillRect(0, 0, canvasNode.width, canvasNode.height);
        ctx.strokeRect(0, 0, canvasNode.width, canvasNode.height);

        if (imageUrl == null) {
            ctx.beginPath();
            ctx.moveTo(0, 0);
            ctx.lineTo(canvasNode.width, canvasNode.height);
            ctx.stroke();
            ctx.beginPath();
            ctx.moveTo(0, canvasNode.height);
            ctx.lineTo(canvasNode.width, 0);
            ctx.stroke();
        }
        var sizeInPreferredUnit = UnitUtils.inchToAnyP(preferredUnit, this.size);
        textNode.text(Utils.numberAsStringWithPrec(sizeInPreferredUnit.x, 4) + "×" + Utils.numberAsStringWithPrec(sizeInPreferredUnit.y, 4) + UnitUtils.unitAsString(preferredUnit));

        untyped __js__("this.n.css")(
            { left: Std.string(position.x) + "px",
              top: Std.string(position.y) + "px",
              width: Std.string(size.x) + "px",
              height: Std.string(size.y) + "px" });
        super.refresh();
    }
}
