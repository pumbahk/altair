package views;

class Tooltip implements Renderable {
    public var renderer(default, null):Renderer;
    public var position(default, default):Point;
    public var text:String;
    
    public function refresh():Void {
        renderer.realize(this);
    }

    public function new(renderer:Renderer) {
        this.renderer = renderer;
        this.position = { x:0., y:0. };
        this.text = "";
    }
}
