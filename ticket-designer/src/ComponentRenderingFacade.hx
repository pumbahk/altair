class ComponentRenderingFacade {
    public var stage(default, null):Stage;
    public var factory(default, null):RendererFactory;

    public function newRenderer(klass:Class<Component>): ComponentRenderer {
        var renderer = cast(factory.create(untyped klass), ComponentRenderer);
        stage.add(renderer);
        return renderer;
    }

    public function new(stage:Stage, factory:RendererFactory) {
        this.stage = stage;
        this.factory = factory;
    }
}
