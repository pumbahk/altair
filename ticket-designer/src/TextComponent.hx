import js.JQuery;

@events(['click'])
class TextComponent extends ComponentBase<TextComponent> {
    public var text(default, default):String;

    public function new(renderer:Renderer<TextComponent>) {
        super(renderer);
        text = '';
    }
}
