package model;

import util.MemorizeTable;

class ElementL1 implements HasID {
    private var _memorize_rels:Bool;
    private var _tbl:Hash<ElementL1>;
    private var _id:String;
    private var _included:Array<String>;
    private var _memorize_tbl:MemorizeTable<Dynamic>;
    private var _name:String;

    public function nortifyDataLinkChanged():Void
    {
        this._memorize_tbl.reset();
    }

    public function new(tbl:Hash<ElementL1>, id:String, included:Array<String>, name:String=null, memorize_rels:Bool = true)
    {
        this._tbl           = tbl;
        this._id            = id;
        this._included      = included;
        this._name          = name;

        this._memorize_tbl = new MemorizeTable< Array<ElementL1> >(memorize_rels);
    }

    public function id():String
    {
        return this._id;
    }

    public function parents():Hash<ElementL1>
    {
        var rt:Hash<ElementL1> = this._memorize_tbl.get("parents", Type.getClass(new Hash<ElementL1>()) );

        if (rt != null) return rt;

        rt = new Hash<ElementL1>();

        for (i in this._included) {
            if (this._tbl.exists(i)) {
                var elm:ElementL1 = this._tbl.get(i);
                rt.set(elm.id(), elm);
                for (j in elm.parents()) {
                    rt.set(j.id(), j);
                }
            }
        }

        this._memorize_tbl.set("parents", rt);

        return rt;
    }

    private function parentXXX<T>(name:String, klass:Class<T>):T
    {

        var rt:T = this._memorize_tbl.get(name, klass);
        if (rt != null) return rt;

        for (i in this.parents()) {
            var class_name = Type.getClassName(Type.getClass(i));
            if (class_name == Type.getClassName(klass)) {
                rt = cast i;
                break;
            }
        }

        this._memorize_tbl.set(name, rt);

        return rt;
    }

    public function name():String
    {
        return this._name;
    }

    public function parentRow():SeatAreaRow
    {
        return this.parentXXX("parentRow", SeatAreaRow);
    }

    public function parentCol():SeatAreaCol
    {
        return this.parentXXX("parentCol", SeatAreaCol);
    }

    public function parentBlock():SeatAreaBlock
    {
        return this.parentXXX("parentBlock", SeatAreaBlock);
    }

    public function parentFloor():SeatAreaFloor
    {
        return this.parentXXX("parentFloor", SeatAreaFloor);
    }

    public function parentGate():SeatAreaGate
    {
        return this.parentXXX("parentGate", SeatAreaGate);
    }
}