package views;

class RendererRegistry {
    var klassesMap:Hash<Hash<Class<Renderer>>>;

    public function addImplementation(renderableKlass:Class<Dynamic>, rendererKlass:Class<Renderer>, ?variant:String) {
        var className = Type.getClassName(renderableKlass);
        var klasses = klassesMap.get(className);
        if (klasses == null)
            klassesMap.set(className, klasses = new Hash());
        klasses.set(variant == null ? '': variant, rendererKlass);
    }

    function lookupImplementationInternal(renderableKlass:Class<Dynamic>, ?options:Dynamic):Class<Renderer> {
        var className = Type.getClassName(renderableKlass);
        var klasses = klassesMap.get(className);
        if (klasses != null) {
            var variant = options != null ? options.variant: '';
            var klass = klasses.get(variant);
            if (klass != null)
                return klass;
        }
        var superKlass = Type.getSuperClass(renderableKlass);
        if (superKlass == null)
            return null;
        return lookupImplementationInternal(cast superKlass, options);
    }

    public function lookupImplementation(renderableKlass:Class<Dynamic>, ?options:Dynamic):Class<Renderer> {
        var klass:Class<Renderer> = lookupImplementationInternal(renderableKlass, options);
        if (klass == null)
            throw new IllegalArgumentException("no implementation is registered for " + Type.getClassName(renderableKlass));
        return klass;
    }

    public function new() {
        klassesMap = new Hash();
    }
}
