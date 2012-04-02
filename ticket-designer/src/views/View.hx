package views;

interface View implements Disposable {
    public var ppi(default, set_ppi):Int;
    public var zoom(default, set_zoom):Float;
    public var viewport(get_viewport, null):Viewport;
    public var stage(get_stage, null):Stage;

    public function pixelToInch(value:Float):Float;
    public function pixelToInchP(value:Point):Point;
    public function inchToPixel(value:Float):Float;
    public function inchToPixelP(value:Point):Point;
    public function anyToPixel(unit:UnitKind, value:Float):Float;
    public function anyToPixelP(unit:UnitKind, value:Point):Point;

    public function dispose():Void;
}
