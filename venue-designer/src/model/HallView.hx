package model;

class HallView {

    private var _model_tbl:Hash<Element>;

    public function new (hall_shape:HallShape, hall:HallModel):Void
    {
        this._model_tbl = new Hash<Element>();

        for (shape in hall_shape) {
            var shape_id:String = shape.id();
            var elm:Element = new Element(this._model_tbl, shape_id);
            elm.setShape(shape);
            this._model_tbl.set(shape_id, elm);
        }

        for (mod in hall) {
            var mod_id:String = mod.id();

            var elm:Element = this._model_tbl.get(mod_id);

            if (elm == null) {
                elm = new Element(this._model_tbl, mod_id);
                this._model_tbl.set(mod_id, elm);
            }

            elm.setModel(mod);
        }
    }

    public function elements():Hash<Element>
    {
        return this._model_tbl;
    }

    public function iterator ()
    {
        return new HallIterator(this);
    }

    private function xxx(type:ElementType):Hash<Element>
    {
        var rt:Hash<Element> = new Hash<Element>();

        for(e in this._model_tbl) {
            if (e.type() == type) {
                rt.set(e.id(), e);
            }
        }

        return rt;
    }

    public function roots():Hash<Element>
    {
        var rt:Hash<Element> = new Hash<Element>();

        for (m in this._model_tbl)
        {
            if (Lambda.count(m.parents()) == 0) rt.set(m.id(), m);
        }

        return rt;
    }

    public function seats():Hash<Element>
    {
        return this.xxx(ElementType.seat);
    }

    public function rows():Hash<Element>
    {
        return this.xxx(ElementType.row);
    }

    public function cols():Hash<Element>
    {
        return this.xxx(ElementType.col);
    }

    public function blocks():Hash<Element>
    {
        return this.xxx(ElementType.block);
    }

    public function floors():Hash<Element>
    {
        return this.xxx(ElementType.floor);
    }

    public function gates():Hash<Element>
    {
        return this.xxx(ElementType.gate);
    }

    public function getById(id:String):Element
    {
        return this._model_tbl.get(id);
    }

    public function getByIds(ids:Array<String>):Hash<Element>
    {
        var rt:Hash<Element> = new Hash<Element>();

        for(id in ids) rt.set(id, this._model_tbl.get(id));

        return rt;
    }

    public function get(selector:String):Hash<Element>
    {
        return null;//selector;
    }

}