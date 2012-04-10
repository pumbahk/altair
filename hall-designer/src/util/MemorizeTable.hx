package util;

class MemorizeTable<T> {

    private var _tbl:Hash<T>;
    private var _enable:Bool;

    public function new (enable:Bool=true) {
        this._enable = enable;

        if (_enable) {
            this._tbl = new Hash<T>();
        }
    }

    public function set<T2>(name:String, obj:T2):T2 {
        if (!this._enable) return null;

        var last:T2    = cast this._tbl.get(name);
        var val:T      = cast obj;

        this._tbl.set(name, val);

        return last;
    }

    public function get<T2>(name:String, klass:Class<T2>):T2 {
        if (!this._enable) return null;

        return cast this._tbl.get(name);
    }

    public function reset():Void {
        for (key in this._tbl.keys())
            this._tbl.remove(key);
    }
}