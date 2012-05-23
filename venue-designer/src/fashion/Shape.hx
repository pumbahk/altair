package fashion;

@:native("Fashion.Shape")
extern interface Shape {
    public function position         (d:Dynamic):Dynamic;
    public function size             (d:Dynamic):Dynamic;
    public function transform        (d1:Dynamic):Void;
    public function addTransform     (d:Dynamic):Void;
    public function resetTransform   ():Void;
    public function style            (d:Dynamic):Void;
    public function addStyle         (d:Dynamic):Void;
    public function resetStyle       ():Void;
    public function displayPosition  ():Void;
    public function displaySize      ():Void;
    public function gravityPosition  ():Void;
    public function hitTest          (d:Dynamic):Bool;
    public function addEvent         (d:Dynamic):Void;
    public function removeEvent      (d:Dynamic):Void;
}