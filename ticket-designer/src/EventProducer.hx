import haxe.rtti.Meta;

class EventProducer {
    public var on(default, null):Dynamic;

    public function new() {
        var on = {};
        var klass:Class<Dynamic> = Type.getClass(this);
        while (klass != EventProducer) {
            var meta = Meta.getType(klass);
            if (meta.events != null) {
                for (eventKind in cast(meta.events, Array<Dynamic>))
                    Reflect.setField(on, eventKind, new EventListeners());
            }
            klass = Type.getSuperClass(klass);
        }
        this.on = on;
    }
}
