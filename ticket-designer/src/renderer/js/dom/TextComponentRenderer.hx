package renderer.js.dom;
import js.JQuery;
import js.JqEvent;

class TextComponentRenderer extends JSDOMRenderer implements Renderer<TextComponent> {
    public function setup():Void {
        n = new JQuery('<div class="component-text"></div>');
        n.bind('mousedown', onPress);
        n.bind('mousemove', onMouseMove);
        n.bind('mouseup', onRelease);
    }

    private function onPress(e:JqEvent) {
    }

    private function onMouseMove(e:JqEvent) {
    }

    private function onRelease(e:JqEvent) {
    }

    public function realize(component:Tcomponent):Void {
        n.text(component.text);
    }

    public function bind(event_kind:EventKind, handler:Event -> Void):Void {
        switch (event_kind) {
        case PRESS:
        case RELEASE:
        }
    }
}
