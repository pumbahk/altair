class MouseEvent extends Event {
    public var position:Point;
    public var leftPressed:Bool;
    public var rightPressed:Bool;

    public function new(source:Dynamic, cause:Dynamic) {
        super(source, cause);
    }
}
