package rendering.js.dom;

class Spi {
    public static var rendererRegistry(get_rendererRegistry, null):RendererRegistry;

    public static function get_rendererRegistry():RendererRegistry {
        if (rendererRegistry == null)
            rendererRegistry = new RendererRegistry();
        return rendererRegistry;
    }
}
