function parse(scanner, handlers, stack) {
  handlers.$stack = stack;
  for (var token = null; token = scanner.do_();) {
    switch (token[0]) {
    case 'string': case 'symbol': case 'number':
      stack.push(token[1]);
      break;
    case 'command':
      switch (token[1]) {
      case 'd':
        stack.push(stack[stack.length - 1]);
        break;
      default:
        var handler = handlers[token[1]];
        if (handler === void(0))
          throw new Error("TSE00002: Unknown command: " + token[1]);
        var arity = handler.length;
        handler.apply(handlers, stack.splice(stack.length - arity, arity));
        break;
      }
    }
  }
}

exports.parse = parse;
