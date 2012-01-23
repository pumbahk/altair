class BasicRendererFactoryImpl implements RendererFactory {
    var klasses:Hash<Class<Renderer>>;

    public function addImplementation(componentKlass:Class<Component>, rendererKlass:Class<Renderer>) {
        klasses.set(Type.getClassName(componentKlass), rendererKlass);
    }

    public function create(componentKlass:Class<Component>):Renderer {
        return untyped Type.createInstance(klasses.get(Type.getClassName(componentKlass)), []);
    }

    public function new() {
        klasses = new Hash<Class<Renderer>>();
    }
}
