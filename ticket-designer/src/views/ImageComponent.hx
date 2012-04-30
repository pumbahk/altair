package views;

class ImageComponent extends Component {
    public var imageUrl(default, default):String;

    override function initialize() {
        super.initialize();
        imageUrl = null;
        size = { x: 0.5, y: 0.5 };
        defaultCursor = MouseCursorKind.POINTER;
    }
}
