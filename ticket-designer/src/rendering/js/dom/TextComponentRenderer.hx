package rendering.js.dom;
import js.JQuery;
import js.JQuery.JqEvent;
import haxe.Firebug;

class TextComponentRenderer extends JSDOMRenderer, implements Renderer {
    static function __init__() {
        JSDOMRendererFactory.addImplementation(TextComponent, TextComponentRenderer);
    }

    private var onPressHandler:Event->Void;
    private var onReleaseHandler:Event->Void;
    private var onMouseMoveHandler:Event->Void;

    public function setup():Void {
        n = new JQuery('<div class="component-text"></div>');
        n.bind('mousedown', onPress);
        n.bind('mousemove', onMouseMove);
        n.bind('mouseup', onRelease);
        n.appendTo(base);
    }

    private function onPress(e:JqEvent) {
        onPressHandler(null);
    }

    private function onMouseMove(e:JqEvent) {
        onMouseMoveHandler(null);
    }

    private function onRelease(e:JqEvent) {
        onReleaseHandler(null);
    }

    public function realize(component:Component):Void {
        n.text(cast(component, TextComponent).text);
    }

    public function bind(event_kind:EventKind, handler:Event -> Void):Void {
        switch (event_kind) {
        case PRESS:
            onPressHandler = handler;
        case RELEASE:
            onReleaseHandler = handler;
        case MOUSEMOVE:
            onMouseMoveHandler = handler;
        }
    }
}
