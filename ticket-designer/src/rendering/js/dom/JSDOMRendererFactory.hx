package rendering.js.dom;

class JSDOMRendererFactory {
    static var klasses:Hash<Class<Renderer>>;

    public static function addImplementation(componentKlass:Class<Component>, rendererKlass:Class<Renderer>) {
        if (klasses == null)
            klasses = new Hash<Class<Renderer>>();
        klasses.set(Type.getClassName(componentKlass), rendererKlass);
    }

    public function create(componentKlass:Class<Component>):Renderer {
        return untyped Type.createInstance(klasses.get(Type.getClassName(componentKlass)), []);
    }

    public function new() {}
}
