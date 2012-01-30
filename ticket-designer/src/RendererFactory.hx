interface RendererFactory {
    public function create(klass:Class<Component>):Renderer;
}
