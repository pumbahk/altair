class Event {
    public var source:Dynamic;
    public var cause:Dynamic;

    public function new(source:Dynamic, cause:Dynamic) {
        this.source = source;
        this.cause = cause;
    }
}
