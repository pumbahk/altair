class TextComponent extends ComponentBase<TextComponent> {
    public var text(default, default):String;
    public var fontSize(default, default):Float;

    public function new(?renderer:ComponentRenderer) {
        super(renderer);
        text = '';
        fontSize = 10.5;
    }
}
