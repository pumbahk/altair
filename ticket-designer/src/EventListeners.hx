class EventListeners {
    private var listeners:Array<EventListener>;

    public function new() {
        listeners = new Array();
    }

    public function do_(listener: EventListener) {
        listeners.push(listener);
    }

    public function call(context:Dynamic, event:Event) {
        var throwables = new Array<Throwable>();

        for (listener in listeners) {
            try {
                Reflect.callMethod(context, listener, [event]);
            } catch (e: Throwable) {
                throwables.push(e);
            }
        }

        if (throwables.length > 0)
            throw new Throwables(throwables);
    }
}
