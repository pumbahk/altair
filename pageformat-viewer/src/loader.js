function Loader (loaders, complete, error, continueOnError) {
  this.loaders = loaders;
  this.complete = complete;
  this.error = error || function () {};
  this.continueOnError = continueOnError || true;
};

Loader.prototype.start = function () {
  var loaders = this.loaders;
  var complete = this.complete;
  var error = this.error;
  var continueOnError = this.continueOnError;

  function check(e) {
    if (e && !continueOnError)
      complete(true);
    if (loaders.length > 0) {
      runLoaders();
    } else {
      complete(false);
    }
  }

  funtion runLoaders() {
    while (loaders.length > 0) {
      (function (loader) {
        loader(
          function () {
            check(false);
          }, function (e) {
            error(e, loader);
            check(true);
          }
        );
      })(loaders.shift());
    }
  }
};

exports.Loader = Loader;
