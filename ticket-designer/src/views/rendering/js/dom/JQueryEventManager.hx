package views.rendering.js.dom;

import js.JQuery;

class JQueryEventManager {
    public var n(default, set_n):JQuery;
    private var handlerHash:Hash<Array<JqEvent->Void>>;

    public function new(?n:JQuery) {
        this.n = n;
        this.handlerHash = new Hash();
    }

    public function bind(eventName:String, handler:JqEvent->Void) {
        var handlers = handlerHash.get(eventName);
        if (handlers == null) { 
            handlers = new Array();
            handlerHash.set(eventName, handlers);
        }
        handlers.push(handler);
        if (n != null)
            n.bind(eventName, handler);
    }

    public function unbind(eventName:String, handler:JqEvent->Void) {
        var handlers = handlerHash.get(eventName);
        if (handlers != null) {
            handlers.remove(handler);
            if (n != null)
                n.unbind(eventName, handler);
        }
        throw new Exception("No such handler");
    }

    public function unbindAllEvents() {
        var prevHandlerHash = handlerHash;
        handlerHash = new Hash();
        if (n != null) {
            for (eventName in prevHandlerHash.keys()) {
                var handlers = prevHandlerHash.get(eventName);
                if (handlers != null) {
                    for (handler in handlers)
                        n.unbind(eventName, handler);
                }
            }
        }
    }

    function set_n(value:JQuery):JQuery {
        if (n != null) {
            for (eventName in handlerHash.keys()) {
                var handlers = handlerHash.get(eventName);
                if (handlers != null) {
                    for (handler in handlers)
                        n.unbind(eventName, handler);
                }
            }
        }
        n = value;
        if (n != null) {
            for (eventName in handlerHash.keys()) {
                var handlers = handlerHash.get(eventName);
                if (handlers != null) {
                    for (handler in handlers)
                        n.bind(eventName, handler);
                }
            }
        }
        return value;
    }
}
