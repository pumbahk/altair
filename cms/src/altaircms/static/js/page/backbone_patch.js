// underscore
if(!_.has){
        // Has own property?
    _.has = function(obj, key) {
        return hasOwnProperty.call(obj, key);
    };
}

// backbone.js
var infoMap = {
    'create': {type: 'POST', sufix: "create"},
    'update': {type: 'POST', sufix: "update"},
    'delete': {type: 'POST', sufix: "delete"},
    'read': {type: 'GET' , sufix: "get"}
};

// REST URL cnage 
/*
           original     :    changed
create ->  POST   /foo  :  POST /foo/create
update ->  PUT    /foo  :  POST /foo/update
delete ->  DELTE  /foo  :  POST /foo/delete
read   ->  GET    /foo  :  GET  /foo/get
*/

Backbone.sync = function(info, model, options) {
    var info = infoMap[info];
    var type = info.type; // method_type
    var url_sufix = info.sufix // url`suffix

    // Default JSON-request options.
    var params = {type: type, dataType: 'json'};

    // Ensure that we have a URL.
    if (!options.url) {
        params.url = getValue(model, 'url') || urlError();
    }
    
    // Put suffix via request type(e.g. update: /foo -> /foo/update)
    params.url += "/"+url_sufix;

    // Ensure that we have the appropriate request data.
    if(type == "POST"){
        params.contentType = 'application/json';
        params.data = JSON.stringify(model.toJSON());
    } else {
        params.data = $.param(model.toJSON());
    }

    // For older servers, emulate JSON by encoding the request into an HTML-form.
    if (Backbone.emulateJSON) {
        params.contentType = 'application/x-www-form-urlencoded';
        params.data = params.data ? {model: params.data} : {};
    }
    // Don't process data on a non-GET request.
    if (params.type !== 'GET' && !Backbone.emulateJSON) {
        params.processData = false;
    }
    // console.dir(params);
    // Make the request, allowing the user to override any Ajax options.
    return $.ajax(_.extend(params, options));
};

// Helper function to get a value from a Backbone object as a property
// or as a function.
var getValue = function(object, prop) {
    if (!(object && object[prop])) return null;
    return _.isFunction(object[prop]) ? object[prop]() : object[prop];
};

// Throw an error when a URL is needed, and none is supplied.
var urlError = function() {
    throw new Error('A "url" property or function must be specified');
};


// Backbone.sync = function(method, model, option){
//     console.log("method:"+method);
//     console.log(JSON.stringify(model));
//     console.log("option:"+option);
// };

// change to each model has add sync method?
