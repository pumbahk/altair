package views;

class RendererRegistry {
    var klassesMap:Hash<Hash<Class<Renderer>>>;

    public function addImplementation(renderableKlass:Class<Renderable>, rendererKlass:Class<Renderer>, ?variant:String) {
        var className = Type.getClassName(renderableKlass);
        var klasses = klassesMap.get(className);
        if (klasses == null)
            klassesMap.set(className, klasses = new Hash());
        klasses.set(variant == null ? '': variant, rendererKlass);
    }

    public function lookupImplementation(renderableKlass:Class<Renderable>, ?options:Dynamic):Class<Renderer> {
        var className = Type.getClassName(renderableKlass);
        var klasses = klassesMap.get(className);
        if (klasses == null)
            throw new IllegalArgumentException("no implementations are registered for " + className);
        var variant = options != null ? options.variant: '';
        var klass = klasses.get(variant);
        if (klass == null)
            throw new IllegalArgumentException("no implementation is registered for " + className + ", variant=" + variant);
        return klass;
    }

    public function new() {
        klassesMap = new Hash();
    }
}
