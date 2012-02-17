class Ruler implements Renderable {
    public var renderer(default, null):Renderer;
    public var offset:Int;
    public var unit:UnitKind;
    public var minimumGraduationWidthInPixel:Float;
    public var graduations:Array<Float>;

    public function refresh():Void {
        renderer.realize(this);
    }

    public function new(renderer:Renderer) {
        this.renderer = renderer;
        unit = MILLIMETER;
        minimumGraduationWidthInPixel = 3;
        graduations = [ 1., 5., 10., 50., 100., 500., 1000., ];
    }
}
