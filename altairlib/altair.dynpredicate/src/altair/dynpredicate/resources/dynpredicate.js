(function (fn) {
    if (typeof module != 'undefined')
        fn(module.exports);
    else if (typeof define != 'undefined' && define.amd !== void(0))
        define(['exports'], fn);
})(function (exports) {
    function unescape(s) {
        return s.replace(/\\./, function (g) {
            c = g[0].substring(1);
            if (c >= '0' && c <= '9')
                return g[0];
            else
                return c;
        });
    }

    function objectToArray(object) {
        var retval = [];
        for (var i in object)
            retval.push(i);
        return retval;
    };

    function clone(object) {
        var retval = new object.constructor();
        for (var k in object) {
            if (object.hasOwnProperty(k))
                retval[k] = object[k];
        }
        return retval;
    };

    var tokenRegexp = /(?:\{([^}]+)\})|([A-Za-z_][0-9A-Za-z_]*)|(<>|<=|>=|=>|=<|<|>|[&(),=+*/-])|(?:"((?:[^"\\]|(?:\\.))*)")|(-?(?:[0-9]+(?:\.[0-9]+)?|\.[0-9]+)(?:[eE][-+]?[0-9]+)?)|([ \t]+)|(\r\n|\r|\n)|(.)/mg;

    var Tokenizer = function () {
        this.initialize.apply(this, arguments);
    };

    Tokenizer.prototype.initialize = function (expr) {
        this.re = tokenRegexp;
        this.eof = false;
        this.line = 1;
        this.column = 1;
        this.stack = [];
        this.expr = expr;
    };

    Tokenizer.prototype.pushback = function (t) {
        this.stack.push(t);
    };

    Tokenizer.prototype.next = function () {
        if (this.stack.length > 0)
            return this.stack.pop();
        if (this.eof)
            return null;
        for (;;) {
            var token = this.re.exec(this.expr);
            if (!token) {
                this.eof = true;
                return ['EOF', null, this.line, this.column];
            }
            var t_var = token[1];
            var t_id = token[2];
            var t_op = token[3];
            var t_str = token[4];
            var t_num = token[5];
            var t_sp = token[6];
            var t_newline = token[7];
            var t_unknown = token[8];
            if (t_var !== void(0)) {
                retval = ['VAR', t_var, this.line, this.column];
                this.column += token[0].length;
                return retval;
            } else if (t_id !== void(0)) {
                retval = ['ID', t_id, this.line, this.column];
                this.column += token[0].length
                return retval;
            } else if (t_op !== void(0)) {
                if (t_op === '=<')
                    t_op = '<=';
                else if (t_op === '=>')
                    t_op = '>=';
                retval = [t_op, t_op, this.line, this.column];
                this.column += token[0].length
                return retval;
            } else if (t_str !== void(0)) {
                t_str = unescape(t_str)
                retval = ['STR', t_str, this.line, this.column];
                this.column += token[0].length;
                return retval;
            } else if (t_num !== void(0)) {
                retval = ['NUM', t_num, this.line, this.column];
                this.column += token[0].length;
                return retval;
            } else if (t_sp !== void(0)) {
                this.column += token[0].length;
            } else if (t_newline !== void(0)) {
                this.column = 1
                this.line += 1
            } else {
                throw new Error('Unexpected character: ' + t_unknown + ' at line ' + this.line + ' column ' + this.column);
            }
        }
    };

    var Node = function () {
        this.initialize.apply(this, arguments);
    };

    Node.prototype.initialize = function (type, line, column, value, children) {
        if (type === void(0))
            type = null;
        if (line === void(0))
            line = 0;
        if (column === void(0))
            column = 0;
        if (value === void(0))
            value = null;
        if (children === void(0))
            children = [];
        this.type = type;
        this.line = line;
        this.column = column;
        this.value = value;
        this.children = children;
        this._visitor_name = 'visit_' + this.type;
    };

    Node.prototype.toString = function () {
        return 'Node(type=' + this.type + ', line=' + this.line + ', column=' + this.column + ', value=' + this.value + ', children=' + this.children + ')';
    };

    Node.prototype.accept = function (visitor, ctx) {
        return visitor[this._visitor_name].call(visitor, this, ctx);
    };

    var associativities = {
        '=': 1,
        '<>': 1,
        '>': 1,
        '<': 1,
        '>=': 1,
        '<=': 1,
        '&': 2,
        '+': 3,
        '-': 3,
        '*': 4,
        '/': 4,
    };

    var nodeNames = {
        '=': 'EQ',
        '<>': 'NE',
        '>': 'GT',
        '<': 'LT',
        '>=': 'GE',
        '<=': 'LE',
        '&': 'CON',
        '+': 'ADD',
        '-': 'SUB',
        '*': 'MUL',
        '/': 'DIV',
    };

    var Parser = function () {
        this.initialize.apply(this, arguments);
    };

    Parser.prototype.initialize = function (t) {
        this.t = t;
    };

    Parser.prototype.expect = function (t, types) {
        if (types[t[0]] === void(0))
            this.raiseParseError(t, types);
    };

    Parser.prototype.raiseParseError = function (t, types) {
        throw new Error(objectToArray(types).join(', ') + ' expected, got ' + t[0] + ' at line ' + t[2] + ' column ' + t[3]);
    };

    Parser.prototype.parseFunctionCallArgs = function () {
        args = []
        for (;;) {
            var p= this.parseExpr({')': 1, ',': 1 });
            if (p[0] !== null)
                args.push(p[0]);
            if (p[1][0] == ')')
                break;
        }
        return args;
    };

    Parser.prototype.parseComp = function (expects) {
        if (expects === void(0))
            expects = null;
        var t0 = this.t.next();
        if (t0[0] == '(') {
            return this.parseExpr({')':1});
        } else if (t0[0] == 'VAR' || t0[0] == 'STR') {
            return [new Node(t0[0], t0[2], t0[3], t0[1]), null];
        } else if (t0[0] == 'NUM') {
            var value = 1. * t0[1];
            if (isNaN(value)) {
                throw new Error('Invalid number: ' + t0[1] + ' at line ' + t0[2] + ' column ' + t0[3]);
            }
            return [new Node(t0[0], t0[2], t0[3], value), null];
        } else if (t0[0] == 'ID') {
            var n = new Node('SYM', t0[2], t0[3], t0[1]);
            var t1 = this.t.next()
            if (t1[0] == '(') {
                return [
                    new Node(
                        'CALL',
                        t0[2],
                        t0[3],
                        null,
                        [
                            n,
                            new Node('TUPLE', t1[2], t1[3], null, this.parseFunctionCallArgs())
                        ]
                    ),
                    null
                ];
            } else {
                this.t.pushback(t1);
                return [n, null];
            }
        } else {
            if (expects === null || !(t0[0] in expects)) {
                var expects = expects === null ? {}: clone(expects);
                expects['ID'] = 1;
                expects['VAR'] = 1;
                expects['STR'] = 1;
                expects['NUM'] = 1;
                expects['('] = 1;
                this.raiseParseError(t0, expects);
            }
            return [null, t0];
        }
    };

    Parser.prototype.parseExprInfixLeft = function (n, expects) {
        if (expects === void(0))
            expects = null;
        var t = this.t.next();
        for (;;) {
            if (associativities[t[0]] === void(0)) {
                if (expects !== null && !(t[0] in expects)) {
                    expects = clone(expects);
                    for (var k in associativities)
                        expects[k] = 1;
                    this.raiseParseError(t, expects);
                }
                break;
            } else {
                var p = this.parseComp();
                p[1] = this.t.next();
                // check if any infix operator follows
                if (associativities[t[0]] < (associativities[p[1][0]] || 0)) {
                    this.t.pushback(p[1]);
                    p = this.parseExprInfixLeft(p[0]);

                    n = new Node(
                        nodeNames[t[0]],
                        t[2],
                        t[3],
                        null,
                        [n, p[0]]
                    );
                } else {
                    n = new Node(
                        nodeNames[t[0]],
                        t[2],
                        t[3],
                        null,
                        [n, p[0]]
                    );
                }
                t = p[1];
            }
        }
        return [n, t];
    };

    Parser.prototype.parseExpr = function (expects) {
        if (expects === void(0))
            expects = null;
        var p = this.parseComp(expects);

        if (p[0] === null)
            return p;
        else
            return this.parseExprInfixLeft(p[0], expects);
    };

    Parser.prototype.parse = function () {
        return this.parseExpr({'EOF': 1})[0];
    };

    exports.Tokenizer = Tokenizer;
    exports.Parser = Parser;

    return exports;
});
