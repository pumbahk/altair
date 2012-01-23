package rendering.js.dom;

import js.JQuery;

class JSDOMRendererFactory { 
    static var klasses:Hash<Class<Renderer>>;
    public var base(default, null):JQuery;

    public static function addImplementation(componentKlass:Class<Component>, rendererKlass:Class<Renderer>) {
        if (klasses == null)
            klasses = new Hash<Class<Renderer>>();
        klasses.set(Type.getClassName(componentKlass), rendererKlass);
    }

    public function create(componentKlass:Class<Component>):Renderer {
        return untyped Type.createInstance(klasses.get(Type.getClassName(componentKlass)), [base]);
    }

    public function new(base:JQuery) {
        this.base = base;        
    }
}
