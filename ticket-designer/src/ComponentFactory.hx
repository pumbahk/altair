class ComponentFactory {
    public var renderingFacade(default, null):ComponentRenderingFacade;

    public function create<T>(klass:Class<T>):T {
        return Type.createInstance(klass, [renderingFacade.newRenderer(untyped klass)]);
    }

    public function new(renderingFacade:ComponentRenderingFacade) {
        this.renderingFacade = renderingFacade;
    }
}
