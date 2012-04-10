class IdentifiableSet<T:Identifiable> /* implements Iterable<T> */ {
    public var length(default, null):Int;

    var items_:Hash<T>;

    public function iterator():Iterator<T> {
        return items_.iterator();
    }

    public function add(item:T) {
        var key = Std.string(item.id);
        if (!items_.exists(key)) {
            length++;
            items_.set(key, item);
            return true;
        } else {
            return false;
        }
    }

    public function remove(item:T) {
        var key = Std.string(item.id);
        if (items_.exists(key)) {
            length--;
            items_.remove(Std.string(item.id));
            return true;
        } else {
            return false;
        }
    }

    public function clear() {
        length = 0;
        items_ = new Hash();
    }

    public function new() {
        length = 0;
        items_ = new Hash();
    }
}
