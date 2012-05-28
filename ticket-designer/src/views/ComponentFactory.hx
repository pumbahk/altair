package views;

class ComponentFactory {
    public var nextId:Int;
    public var stage(default, null):Stage;
    public var rendererFactory(default, null):RendererFactory;

    public function create<T>(klass:Class<T>, ?options:Dynamic):T {
        var renderer = cast(rendererFactory.create(untyped klass, options), ComponentRenderer);
        return Type.createInstance(klass, [nextId++, renderer]);
    }

    public function new(rendererFactory:RendererFactory) {
        this.rendererFactory = rendererFactory;
        this.nextId = 1;
    }
}
