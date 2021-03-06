class Throwables implements Throwable {
    private var throwables_: Array<Throwable>;

    public var message(get_message, null): String;
    public var cause(get_cause, null): Throwable;

    public function new(throwables: Array<Throwable>) {
        this.throwables_ = throwables;
    }

    public function push(throwable: Throwable) {
        this.throwables_.push(throwable);
    }

    public function toString() {
        var retval:String = "";
        for (throwable in throwables_) {
            retval += throwable.toString();
            retval += "\n--\n";
        }
        return retval;
    }

    private function get_message(): String {
        return "multiple throwables";
    }

    private function get_cause(): Throwable {
        return null;
    }
}
