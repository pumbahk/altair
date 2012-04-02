interface Command {
    public var data(get_data, null):Dynamic;

    private function get_data():Dynamic;

    public function do_():Void;

    public function undo():Void;
}
