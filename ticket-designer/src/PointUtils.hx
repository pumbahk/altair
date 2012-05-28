class PointUtils {
    public static function add(a:Point, b:Point) {
        return { x:a.x + b.x, y:a.y + b.y };
    }

    public static function sub(a:Point, b:Point) {
        return { x:a.x - b.x, y:a.y - b.y };
    }
}
