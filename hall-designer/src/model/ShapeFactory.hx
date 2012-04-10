package model;

class ShapeFactory {

    private static var _shape_class_tbl:Dynamic = {
        rect:   ShapeRect,
        path:   ShapePath,
        circle: ShapeCircle
    };

    private var _tbl:Hash<Shape>;

    public function new (tbl:Hash<Shape>):Void
    {
        this._tbl = tbl;
    }

    public function create (id:String, src:Dynamic):Shape
    {
        var shape_type:String = cast(Reflect.field(src, "shape"), String);
        var data:Dynamic = Reflect.field(src, "data");

        var attr:Hash<Dynamic> = new Hash<Dynamic>();

        for (d in Reflect.fields(data))
        {
            attr.set(d, Reflect.field(data, d));
        }

        var klass:Class<Shape> = Reflect.field(ShapeFactory._shape_class_tbl, shape_type);
        var shape:Shape = Type.createInstance(klass, [id, attr]);

        this._tbl.set(id, shape);
        return shape;
    }
}