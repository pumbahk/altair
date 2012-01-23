class RenderingFacade {
    public var manager(default, null):RenderingManager;
    public var factory(default, null):RendererFactory;

    public function newRenderer(klass:Class<Component>): Renderer {
        var renderer = factory.create(klass);
        manager.addRenderer(renderer);
        return renderer;
    }

    public function new(manager:RenderingManager, factory:RendererFactory) {
        this.manager = manager;
        this.factory = factory;
    }
}
