package model;

class SeatArea extends ElementL1 {

    public function children():Hash<ElementL1> {
        var rt:Hash<ElementL1> = this._memorize_tbl.get("children", Type.getClass(new Hash<ElementL1>()) );
        if (rt != null) return rt;

        rt = new Hash<ElementL1>();

        for(elm in this._tbl) {
            var flag:Bool = false;
            for (j in elm.parents()) {
                if (j.id() == this._id) {
                    flag = true;
                    break;
                }
            }
            if (!flag) continue;

            rt.set(elm.id(), elm);

            if (Std.is(elm, SeatArea)) {
                for (j in cast(elm, SeatArea).children()) {
                    rt.set(j.id(), j);
                }
            }

        }

        this._memorize_tbl.set("children", rt);

        return rt;
    }

    private function childXXX<T>(name:String, klass:Class<T>):Hash<T> {

        var rt:Hash<T> = this._memorize_tbl.get(name, Type.getClass(new Hash<T>()));
        if (rt != null) return rt;

        rt = new Hash<T>();

        for (i in this.children()) {
            if (Type.getClassName(Type.getClass(i)) == Type.getClassName(klass)) {
                var elm:T = cast i;
                rt.set(i.id(), elm);
            }
        }

        this._memorize_tbl.set(name, rt);

        return rt;
    }

    public function childSeats():Hash<Seat> {
        return this.childXXX("childSeats", Seat);
    }

    public function childRows():Hash<SeatAreaRow> {
        return this.childXXX("childAreaRow", SeatAreaRow);
    }

    public function childCols():Hash<SeatAreaCol> {
        return this.childXXX("childAreaCol", SeatAreaCol);
    }

    public function childBlocks():Hash<SeatAreaBlock> {
        return this.childXXX("childAreaBlock", SeatAreaBlock);
    }

    public function childFloors():Hash<SeatAreaFloor> {
        return this.childXXX("childAreaFloor", SeatAreaFloor);
    }

    public function childGates():Hash<SeatAreaGate> {
        return this.childXXX("childGates", SeatAreaGate);
    }
}