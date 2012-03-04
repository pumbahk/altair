package rendering.js.dom;

class Spi {
    public static var rendererFactory(get_rendererFactory, null):BasicRendererFactoryImpl;

    public static function get_rendererFactory():BasicRendererFactoryImpl {
        if (rendererFactory == null)
            rendererFactory = new BasicRendererFactoryImpl();
        return rendererFactory;
    }
}
