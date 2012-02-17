class BasicStageImpl<Trenderer:ComponentRenderer, Tview:View> implements Stage {
    public var renderers(get_renderers, null):Iterable<ComponentRenderer>;
    public var view(get_view, null):View;
    public var view_:Tview;
    var renderers_:Array<Trenderer>;

    public function add(renderer:ComponentRenderer):Void {
        renderers_.push(untyped renderer);
        renderer.stage = this;
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
        this.renderers_ = new Array<Trenderer>();
    }
}
