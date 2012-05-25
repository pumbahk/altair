package model;

class Element implements HasID {

    private static var _type_class_tbl:Dynamic = {
        Seat:          ElementType.seat,
        SeatAreaRow:   ElementType.row,
        SeatAreaCol:   ElementType.col,
        SeatAreaBlock: ElementType.block,
        SeatAreaFloor: ElementType.floor,
        SeatAreaGate:  ElementType.gate
    };

    private var _id:String;
    private var _model:ElementL1;
    private var _shape:Shape;
    private var _tbl:Hash<Element>;
    private var _style:Dynamic;
    private var _z_index:Int;

    public function new (tbl:Hash<Element>, id:String):Void
    {
        this._tbl = tbl;
        this._id = id;
        this._model = null;
        this._shape = null;
        this._style = {};
        this._z_index = 0;
    }

    public function id():String
    {
        return this._id;
    }

    public function name():String
    {
        var n:String = null;
        if (this._model != null) {
            n = this._model.name();
        }
        return n;
    }

    public function zIndex(idx:Int=null):Int
    {
        if (idx != null) {
            this._z_index = idx;
        }
        return this._z_index;
    }

    // todo memorize
    public function type():ElementType {
        var rt:ElementType = null;

        if (this._model != null) {
            var c:String = Type.getClassName(Type.getClass(this._model));
            c = c.substr(6); // cut off "model."
            rt = Reflect.field(Element._type_class_tbl, c);

        } else if (this._shape != null) {
            rt = ElementType.plainShape;

        }

        return (rt == null) ? ElementType.unknown : rt;
    }

    public function hasShape():Bool
    {
        return (this._shape != null);
    }

    public function setModel(model:ElementL1):Void
    {
        this._model = model;
    }

    public function setShape(shape:Shape):Void
    {
        this._shape = shape;
    }

    public function getShape():Shape
    {
        return this._shape;
    }

    public function getModel():ElementL1
    {
        return this._model;
    }

    public function nortifyDataLinkChanged():Void
    {
        if (this._model != null) {
            this._model.nortifyDataLinkChanged();
        }
    }

    private function getElements(ids:Array<String>): Hash<Element>
    {
        var rt:Hash<Element> = new Hash<Element>();

        if (ids != null) {
            for (id in ids) {
                rt.set(id, this._tbl.get(id));
            }
        }

        return rt;
    }

    private function getIDArray(objs:Hash<HasID>):Array<String>
    {
        var rt:Array<String> = new Array<String>();
        for (obj in objs) rt.push(obj.id());
        return rt;
    }

    public function parents():Hash<Element>
    {
        // Unnecessary cast
        if (this._model != null) {
            return this.getElements(this.getIDArray(cast this._model.parents()));
        } else {
            return new Hash<Element>();
        }
    }

    public function parentRow():Element
    {
        if (this._model != null) {
            var e:ElementL1 = this._model.parentRow();
            if (e != null) return this._tbl.get(e.id());
        }

        return null;

    }

    public function parentCol():Element
    {
        if (this._model != null) {
            var e:ElementL1 = this._model.parentCol();
            if (e != null) return this._tbl.get(e.id());
        }
        return null;
    }

    public function parentBlock():Element
    {
        if (this._model != null) {
            var e:ElementL1 = this._model.parentBlock();
            if (e != null) return this._tbl.get(e.id());
        }
        return null;
    }

    public function parentFloor():Element
    {
        if (this._model != null) {
            var e:ElementL1 = this._model.parentFloor();
            if (e != null) return this._tbl.get(e.id());
        }
        return null;
    }

    public function parentGate():Element
    {
        if (this._model != null) {
            var e:ElementL1 = this._model.parentGate();
            if (e != null) return this._tbl.get(e.id());
        }
        return null;
    }

    private function getChildXXX<T>(fn:SeatArea->Hash<T>):Hash<Element>
    {
        if (Std.is(this._model, SeatArea)) {

            var elm:SeatArea = cast(this._model, SeatArea);
            var children:Hash<T> = fn(elm);

            // Unnecessary cast
            return this.getElements(this.getIDArray(cast children));
        }
        return new Hash<Element>();
    }

    public function children():Hash<Element>
    {
        return this.getChildXXX(
            function(elm:SeatArea):Hash<ElementL1> { return elm.children(); });
    }

    public function childSeats():Hash<Element>
    {
        return this.getChildXXX(
            function(elm:SeatArea):Hash<Seat> { return elm.childSeats(); });
    }

    public function childRows():Hash<Element>
    {
        return this.getChildXXX(
            function(elm:SeatArea):Hash<SeatAreaRow> { return elm.childRows(); });
    }

    public function childCols():Hash<Element>
    {
        return this.getChildXXX(
            function(elm:SeatArea):Hash<SeatAreaCol> { return elm.childCols(); });
    }

    public function childBlocks():Hash<Element>
    {
        return this.getChildXXX(
            function(elm:SeatArea):Hash<SeatAreaBlock> { return elm.childBlocks(); });
    }

    public function childGates():Hash<Element>
    {
        return this.getChildXXX(
            function(elm:SeatArea):Hash<SeatAreaGate> { return elm.childGates(); });
    }

    public function style(style:Dynamic=null):Dynamic
    {
        if (style != null) {
            this._style = style;
        }

        return this._style;
    }
}