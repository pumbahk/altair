class BasicRendererFactoryImpl implements RendererFactory {
    var nextId:Int;
    var registry:RendererRegistry;
    var view:View;

    public function create(renderableKlass:Class<Renderable>, ?options:Dynamic):Renderer {
        return untyped Type.createInstance(
                registry.lookupImplementation(renderableKlass, options),
                [ nextId++, view ]);
    }

    public function new(view:View, registry:RendererRegistry) {
        this.view = view;
        this.registry = registry;
        this.nextId = 1;
    }
}
