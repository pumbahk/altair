package views;

class ImageComponent extends Component {
    public var imageUrl(default, default):String;
    public var preferredUnit(default, default):UnitKind;

    override function initialize() {
        super.initialize();
        imageUrl = null;
        size = { x: 0.5, y: 0.5 };
        preferredUnit = UnitKind.INCH;
        defaultCursor = MouseCursorKind.POINTER;
    }
}
