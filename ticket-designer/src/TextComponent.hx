import js.JQuery;

class TextComponent extends ComponentBase<TextComponent> {
    public var text(default, default):String;

    public function new(?renderer:Renderer) {
        super(renderer);
        text = '';
    }
}
