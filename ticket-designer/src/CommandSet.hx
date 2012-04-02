class CommandSet implements Command {
    public var data(get_data, null):Dynamic;
    public var commands(default, null):Array<Command>;

    public function get_data():Dynamic {
        return commands;
    }

    public function do_():Void {
        for (command in commands)
            command.do_();
    }

    public function undo():Void {
        var i:Int = commands.length;
        while (--i >= 0) {
            commands[i].undo();
        }
    }

    public function add(command:Command):Void {
        commands.push(command);
    }

    public function new() {
        commands = new Array<Command>();
    }
}
