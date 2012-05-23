package model;

class HallShape {
    private var _model_tbl:Hash<Shape>;

    public function new (src:Dynamic):Void {

        this._model_tbl = new Hash<Shape>();

        var fac:ShapeFactory = new ShapeFactory(this._model_tbl);

        for (i in Reflect.fields(src)) {
            fac.create(i, Reflect.field(src, i));
        }
    }

    public function shapes():Hash<Shape> {
        return this._model_tbl;
    }

    public function shape(id:String):Shape {
        return this._model_tbl.get(id);
    }

    public function iterator ()
    {
        return this._model_tbl.iterator();
    }
}