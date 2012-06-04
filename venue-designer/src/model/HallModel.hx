package model;

class HallModel {

    private var _model_tbl:Hash<ElementL1>;

    public function new (src:Dynamic):Void {

        this._model_tbl = new Hash<ElementL1>();

        var fac:ElementL1Factory = new ElementL1Factory(this._model_tbl);

        for (i in Reflect.fields(src)) {
            fac.create(i, Reflect.field(src, i));
        }
    }

    private function xxx<T>(klass:Class<T>):Hash<T> {
        var rt:Hash<T> = new Hash<T>();

        for (i in this._model_tbl) {
            if (Type.getClassName(Type.getClass(i)) == Type.getClassName(klass)) {
                var elm:T = cast i;
                rt.set(i.id(), elm);
            }
        }

        return rt;
    }

    public function elements():Hash<ElementL1>
    {
        return this._model_tbl;
    }

    public function roots():Hash<ElementL1>
    {
        var rt:Hash<ElementL1> = new Hash<ElementL1>();

        for (m in this._model_tbl)
        {
            if (Lambda.count(m.parents()) == 0) rt.set(m.id(), m);
        }

        return rt;
    }

    public function rows():Hash<SeatAreaRow>
    {
        return this.xxx(SeatAreaRow);
    }

    public function cols():Hash<SeatAreaCol>
    {
        return this.xxx(SeatAreaCol);
    }

    public function blocks():Hash<SeatAreaBlock>
    {
        return this.xxx(SeatAreaBlock);
    }

    public function floors():Hash<SeatAreaFloor>
    {
        return this.xxx(SeatAreaFloor);
    }

    public function gates():Hash<SeatAreaGate>
    {
        return this.xxx(SeatAreaGate);
    }

    public function seats():Hash<Seat>
    {
        return this.xxx(Seat);
    }

    public function iterator ()
    {
        return this._model_tbl.iterator();
    }
}