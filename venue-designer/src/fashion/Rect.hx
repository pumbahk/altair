package fashion;

@:native("Fashion.Rect")
extern class Rect implements Shape {
    public function new              (x:Float, y:Float, width:Float, height:Float):Void;

    @:overload(function():Dynamic{})
    public function position         (d:Dynamic):Dynamic;

    @:overload(function():Dynamic{})
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