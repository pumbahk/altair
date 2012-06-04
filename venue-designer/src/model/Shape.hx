package model;

class Shape implements HasID {

    private var _id:String;
    private var _attrs:Hash<Dynamic>;

    public function new(id:String, attrs:Hash<Dynamic>) {
        this._id = id;
        this._attrs = attrs;
    }

    public function id() {
        return this._id;
    }

    public function attrs(att:Dynamic=null) {
        if (att != null) {
            for (i in Reflect.fields(att)) {
                this._attrs.set(i, Reflect.field(att, i));
            }
        }
        return this._attrs;
    }

    public function getAttr(key:String):Dynamic {
        return this._attrs.get(key);
    }

    public function setAttr<T>(key:String, data:T):T {
        this._attrs.set(key, untyped data);
        return data;
    }

    public function attr<T>(key:String, d:T=null):T {
        if (d != null) return this.setAttr(key, d);
        else return cast this.getAttr(key);
    }

}