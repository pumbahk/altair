interface RendererFactory {
    public function create(klass:Class<Renderable>, ?options:Dynamic):Renderer;
}
