class ComponentFactory {
    public var stage(default, null):Stage;
    public var rendererFactory(default, null):RendererFactory;

    public function create<T>(klass:Class<T>):T {
        var renderer = cast(rendererFactory.create(untyped klass), ComponentRenderer);
        stage.add(renderer);
        return Type.createInstance(klass, [renderer]);
    }

    public function new(stage:Stage, rendererFactory:RendererFactory) {
        this.stage = stage;
        this.rendererFactory = rendererFactory;
    }
}
