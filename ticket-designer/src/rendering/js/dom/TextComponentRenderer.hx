package rendering.js.dom;
import js.JQuery;
import js.JQuery.JqEvent;
import haxe.Firebug;

class TextComponentRenderer extends JSDOMRenderer {
    static function __init__() {
        JSDOMRendererFactory.addImplementation(TextComponent, TextComponentRenderer);
    }

    public override function setup(manager:RenderingManager, id:Int):Void {
        n = new JQuery('<div class="component-text"></div>');
        super.setup(manager, id);
    }

    public override function realize(component:Component):Void {
        untyped __js__("this.n.css")(
            { left: Std.string(component.position.x) + "px",
              top: Std.string(component.position.y) + "px"});
        n.text(cast(component, TextComponent).text);
    }
}
