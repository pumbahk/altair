package views;

class BoundingBox implements Renderable {
    public var renderer(default, null):Renderer;
    public var position(default, default):Point;
    public var size(default, default):Point;
    public var imageUrl:String;
    
    public function refresh():Void {
        renderer.realize(this);
    }

    public function new(renderer:Renderer) {
        this.renderer = renderer;
        this.position = { x:0., y:0. };
        this.size = { x:5., y:2. };
        this.imageUrl = null;
    }
}

