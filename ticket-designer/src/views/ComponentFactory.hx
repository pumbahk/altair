package views;

class ComponentFactory {
    public var nextId:Int;
    public var stage(default, null):Stage;
    public var rendererFactory(default, null):RendererFactory;

    public function create<T>(klass:Class<T>, ?options:Dynamic):T {
        var renderer = cast(rendererFactory.create(untyped klass, options), ComponentRenderer);
        stage.add(renderer);
        return Type.createInstance(klass, [this, nextId++, renderer]);
    }

    public function new(stage:Stage, rendererFactory:RendererFactory) {
        this.stage = stage;
        this.rendererFactory = rendererFactory;
        this.nextId = 1;
    }
}
