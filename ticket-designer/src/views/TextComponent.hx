package views;

class TextComponent extends Component {
    public var text(default, default):String;
    public var fontSize(default, default):Float;

    override function initialize() {
        super.initialize();
        text = '';
        fontSize = 10.5;
        size = { x: 0.25, y: 0.25 };
        defaultCursor = MouseCursorKind.POINTER;
    }
}
