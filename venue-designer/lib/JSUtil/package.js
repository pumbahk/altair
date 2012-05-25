var JSUtil = (function() {
  var _JSUtil = {};

  include("util.error.js");
  include("Console.js");
  include("JSONParser.js");

  _JSUtil.JSONParser = JSONParser;
  _JSUtil.Console = Console;

  return _JSUtil;

})();
