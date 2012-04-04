package views;

interface RendererFactory {
    public function create(klass:Class<Dynamic>, ?options:Dynamic):Renderer;
}
