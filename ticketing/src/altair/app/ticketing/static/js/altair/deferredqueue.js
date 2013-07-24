if (!window.altair){
    window.altair = {};
}
// how to use
/*
var q = new Deferred();
q.enqueue(function(){...}, "global");
q.enqueue(function(){...}, "global");
q.enqueue(function(){...});

q.cancel(function(t){return t.group == "global"});

q.enqueue_only_me(function(){..}, 
                  function(t){return t.group == "global"}, 
                  "global");
q.fire();

todo: 
  compaction
  prirotigy
*/
(function(altair){
    var Task = function(fn, group){
        this.fn = fn; // fn is deferred.
        this.group = group;
    };

    var Deferred = function(autofire){
        this.q = [];
        this.runnnigp = false;
        this.autofile = autofire;
    };
    
    Deferred.prototype.enqueue = function(fn, group){
        this.q.push(new Task(fn, priority, group));
        if(this.autofire){
            this.fire();
        }
    };

    Deferred.prototype.fire = function(){
        if(!this.runnnigp){
            this.runnnigp = true;
            this.consume();
        }
    };

    Deferred.prototype.consume = function(){
        if(!this.runnnigp || this.q.length <= 0){
            this.runnnigp = false;            
            return;
        }

        var q = this.q;
        var task = q.shift();
        while(!task){
            task = q.shift();
        }
        return task.fn().always(this.consume.bind(this));
    }; 

    Deferred.prototype.cancel = function(predicate){
        var prev_status = this.runnigp;
        this.runnnigp = false; //for safety.

        var q = this.q;
        var canceled = [];
        for(var i=0, j=q.length; i<j; i++){
            if(predicate(q[i])){
                canceled.push(q[i]);
                q[i] = null;
            }
        }
        if (prev_status){
            this.fire();
        }
        return canceled;
    };

    // Deferred.prototype.rebalance(i, task){
    //     throw "not implemented yet";
    // }
    altair.DeferredQueue = DeferredQueue;
})(window.altair);
