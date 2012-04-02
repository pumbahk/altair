package rendering.js.dom;

import js.JQuery;

interface MouseEventsHandler {
    public var id(default, null):Int;
    public var n(default, null):JQuery;
    public var onPress:JqEvent->Void;
    public var onRelease:JqEvent->Void;
    public var onMouseMove:JqEvent->Void;
    public var onMouseOut:JqEvent->Void;
}
