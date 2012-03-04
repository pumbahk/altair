class BasicStageImpl<Trenderer:ComponentRenderer, Tview:View> implements Stage {
    public var renderers(get_renderers, null):Iterable<ComponentRenderer>;
    public var view(get_view, null):View;
    public var view_:Tview;
    var renderers_:Hash<Trenderer>;

    public function add(renderer:ComponentRenderer):Void {
        renderers_.set(Std.string(renderer.id), untyped renderer);
        renderer.stage = this;
    }

    public function remove(renderer:ComponentRenderer):Void {
        renderer.stage = null;
        renderers_.remove(Std.string(renderer.id));
    }

    public function dispose():Void {
        for (renderer in renderers_) {
            var throwables = new Array<Throwable>();
            try {
                renderer.dispose();
            } catch (e:Throwable) {
                throwables.push(e); 
            }
            if (throwables.length > 0)
                throw new Throwables(throwables);
        }
    }

    private function get_renderers():Iterable<ComponentRenderer> {
        return renderers_;
    }

    private function get_view():View {
        return view_;
    }

    public function new(view:Tview) {
        this.view_ = view;
        this.renderers_ = new Hash();
    }
}
