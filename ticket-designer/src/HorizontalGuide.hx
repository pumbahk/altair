class HorizontalGuide extends ComponentBase<TextComponent> {
    public function new(renderer:ComponentRenderer) {
        super(renderer);
        defaultCursor = MouseCursorKind.CROSSHAIR;
    }
}
