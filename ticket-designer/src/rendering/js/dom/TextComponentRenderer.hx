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
        n.appendTo(cast(manager, JSDOMRenderingManager).base);
    }

    private function createMouseEvent(e:JqEvent):MouseEvent {
        var manager_ = cast(manager, JSDOMRenderingManager);
        return {
            source: this,
            cause: e,
            position:{ x:e.pageX - manager_.basePageOffset.x,
                       y:e.pageY - manager_.basePageOffset.y },
            left:(e.which & 1) != 0,
            middle:(e.which & 2) != 0,
            right:(e.which & 3) != 0 };
    }

    private function onPress(e:JqEvent) {
        onPressHandler(createMouseEvent(e));
    }

    private function onMouseMove(e:JqEvent) {
        onMouseMoveHandler(createMouseEvent(e));
    }

    private function onRelease(e:JqEvent) {
        onReleaseHandler(createMouseEvent(e));
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
