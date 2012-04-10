package views.rendering.js.dom;

import js.JQuery;

class MouseEventsHandler {
    public var id:Int;
    public var n(default, null):JQuery;
    public var onPress(default, null):JqEvent->Void;
    public var onRelease(default, null):JqEvent->Void;
    public var onMouseMove(default, null):JqEvent->Void;
    public var onMouseOut(default, null):JqEvent->Void;

    public function getHandlerFunctionFor(eventKind:EventKind) {
        switch (eventKind) {
        case PRESS:
            return onPress;
        case RELEASE:
            return onRelease;
        case MOUSEMOVE:
            return onMouseMove;
        case MOUSEOUT:
            return onMouseOut;
        }
    }

    public function new(n:JQuery,
                        onPress:JqEvent->Void, onRelease:JqEvent->Void,
                        onMouseMove:JqEvent->Void, onMouseOut:JqEvent->Void) {
        this.n = n;
        this.onPress = onPress;
        this.onRelease = onRelease;
        this.onMouseMove = onMouseMove;
        this.onMouseOut = onMouseOut;
    }
}
