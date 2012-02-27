package rendering.js.dom;
import js.JQuery;

class JSDOMComponentRenderer extends JSDOMRenderer, implements ComponentRenderer{
    var stage_:JSDOMStage;
    public var opacity:Float;
    public var stage(get_stage, set_stage):Stage;

    private function get_stage():Stage {
        return stage_;
    }

    private function set_stage(stage:Stage):Stage {
        if (n != null)
            n.detach();
        stage_ = cast(stage, JSDOMStage);
        view = stage_.view_;
        if (n != null)
            n.appendTo(stage_.base);
        return stage;
    }

    public override function refresh(): Void {
        untyped __js__("this.n.css")("opacity", Std.string(opacity));
    }

    override function createMouseEvent(e:JqEvent):MouseEvent {
        return {
            source: this,
            cause: e,
            position: view_.pixelToInchP(
                { x: cast(e.pageX, Float) - stage_.basePageOffset.x,
                  y: cast(e.pageY, Float) - stage_.basePageOffset.y }),
            left: (e.which & 1) != 0,
            middle: (e.which & 2) != 0,
            right: (e.which & 3) != 0 };
    }

    public function new(id:Int) {
        super(id);
        this.opacity = 1.0;
        this.stage_ = null;
    }
}
