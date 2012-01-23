class Exception implements Throwable {
    private var message_: String;
    private var cause_: Throwable;

    public var message(get_message, null): String;
    public var cause(get_cause, null): Throwable;

    public function new(?message: String, cause: Throwable) {
        this.message_ = message;
        this.cause_ = cause;
    }

    private function get_message(): String {
        return message_;
    }

    private function get_cause(): Throwable {
        return cause_;
    }
}
