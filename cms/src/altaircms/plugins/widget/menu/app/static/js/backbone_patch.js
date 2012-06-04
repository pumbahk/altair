// underscore
if(!_.has){
        // Has own property?
    _.has = function(obj, key) {
        return hasOwnProperty.call(obj, key);
    };
}
