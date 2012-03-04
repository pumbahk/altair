interface View implements Disposable {
    public var ppi(default, set_ppi):Int;
    public var zoom(default, set_zoom):Float;
    public var viewport(get_viewport, null):Viewport;
    public var stage(get_stage, null):Stage;

    public function dispose():Void;
}
