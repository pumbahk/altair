package model;

class ElementL1Factory {

    private static var _area_class_tbl:Dynamic = {
        block: SeatAreaBlock,
        floor: SeatAreaFloor,
        gate : SeatAreaGate,
        row  : SeatAreaRow,
        col  : SeatAreaCol
    };

    private var _tbl:Hash<ElementL1>;

    public function new (tbl:Hash<ElementL1>)
    {
        this._tbl = tbl;
    }

    public function create(id:String, src:Dynamic):ElementL1
    {
        var type:String = cast(Reflect.field(src, "type"), String);
        var included:Array<String> = Reflect.field(src, "included");

        var elm:ElementL1 = null;

        if (type == "seat") {
            elm = new Seat(this._tbl, id, included);

        } else if (type == "area") {
            var area_type:String = cast(Reflect.field(src, "area-type"), String);
            var name:String = cast(Reflect.field(src, "name"), String);

            var klass:Class<SeatArea> = Reflect.field(ElementL1Factory._area_class_tbl, area_type);

            elm = Type.createInstance(klass, [this._tbl, id, included, name]);

        } else {
            throw "Unknown type specified (" + type + ").";
        }

        this._tbl.set(id, elm);


        return elm;
    }

}

