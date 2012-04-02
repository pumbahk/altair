package views;

class VerticalGuide extends ComponentBase<TextComponent> {
    public function new(renderer:ComponentRenderer) {
        super(renderer);
        defaultCursor = MouseCursorKind.CROSSHAIR;
    }
}
