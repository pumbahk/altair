package views.rendering.js.dom;

import js.JQuery;
import js.Lib;

class MouseEventsHandlerManager {
    var nextId:Int;
    var capturing:MouseEventsHandler;
    var mouseEventsHandlers:Hash<MouseEventsHandler>;
    var eventHandlerHash:Hash<JqEvent->Bool>;
    static var eventNames = [ 'mousedown', 'mouseup', 'mousemove', 'mouseout' ];

    public function captureMouse(mouseEventsHandler:MouseEventsHandler):Void {
        if (capturing != null)
            throw new IllegalStateException("mouse has already been captured by " + capturing);
        capturing = mouseEventsHandler;
        if (capturing.onPress != null)
            new JQuery(Lib.document).bind('mousedown', capturing.onPress);
        if (capturing.onRelease != null)
            new JQuery(Lib.document).bind('mouseup', capturing.onRelease);
        if (capturing.onMouseMove != null)
            new JQuery(Lib.document).bind('mousemove', capturing.onMouseMove);
    }

    public function releaseMouse():Void {
        if (capturing == null)
            return;
        if (capturing.onPress != null)
            new JQuery(Lib.document).unbind('mousedown', capturing.onPress);
        if (capturing.onRelease != null)
            new JQuery(Lib.document).unbind('mouseup', capturing.onRelease);
        if (capturing.onMouseMove != null)
            new JQuery(Lib.document).unbind('mousemove', capturing.onMouseMove);
        capturing = null;
    }

    private static inline function getEventNameFor(eventKind:EventKind) {
        return eventNames[Type.enumIndex(eventKind)];
    }

    private static inline function buildEventHandlerKey(mouseEventsHandler:MouseEventsHandler, eventName:String):String {
        return Std.string(mouseEventsHandler.id) + ":" + eventName;
    }

    public function bindEvent(mouseEventsHandler:MouseEventsHandler, eventKind:EventKind) {
        var eventName = getEventNameFor(eventKind);
        var key = buildEventHandlerKey(mouseEventsHandler, eventName);
        if (eventHandlerHash.get(key) != null)
            throw new IllegalStateException("event " + eventName + " is already bound");
        var handlerFunction = mouseEventsHandler.getHandlerFunctionFor(eventKind);

        var closure = function(e:JqEvent) {
            if (capturing == null
                    || capturing.n[0] == e.target) {
                handlerFunction(e);
                return false;
            }
            return true;
        };
        eventHandlerHash.set(key, closure);
        mouseEventsHandler.n.bind(eventName, cast closure);
    }

    public function unbindEvent(mouseEventsHandler:MouseEventsHandler, eventKind:EventKind) {
        var eventName = getEventNameFor(eventKind);
        var key = buildEventHandlerKey(mouseEventsHandler, eventName);
        var handlerFunction = eventHandlerHash.get(key);
        if (handlerFunction == null)
            throw new IllegalStateException("event " + eventName + " is not bound yet");
        mouseEventsHandler.n.unbind(eventName, cast handlerFunction);
        eventHandlerHash.remove(key);
    }

    public function registerHandler(mouseEventsHandler:MouseEventsHandler):MouseEventsHandler {
        mouseEventsHandler.id = nextId++;
        mouseEventsHandlers.set(Std.string(mouseEventsHandler.id), mouseEventsHandler);
        return mouseEventsHandler; 
    }

    public function unregisterHandler(mouseEventsHandler:MouseEventsHandler):Void {
        mouseEventsHandlers.remove(Std.string(mouseEventsHandler.id));
    }

    public function new() {
        nextId = 1;
        capturing = null;
        mouseEventsHandlers = new Hash();
        eventHandlerHash = new Hash();
    }

}
