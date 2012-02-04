var calc = (function(){
    var Unit = function(val, unit){
        this.unit = unit;
        this.val = val;
    };

    Unit.prototype.add = function(other){
        if(this.unit == other.unit){
            return new Unit(this.val+other.val, this.unit);
        } else {
            var fmt = "invalid unit type @s@ != @t@";
            throw fmt.replace("@s@", this.unit).replace("@t@", other.unit);
        }
    };

    Unit.prototype.sub = function(other){
        if(this.unit == other.unit){
            return new Unit(this.val+other.val, this.unit);
        } else {
            var fmt = "invalid unit type @s@ != @t@";
            throw fmt.replace("@s@", this.unit).replace("@t@", other.unit);
        }
    };

    Unit.prototype.toString = function(){
        return String(this.val) + this.unit;
    }
    var _re = /(\d+)(.*)/;

    var toUnit = function(str){
        var m = str.match(_re);
        if(!!m){
            return new Unit(Number(m[1]), m[2]);
        } else{
            throw "invalid paramater passed @s@.".replace("@s@", str);
        }
    };
    return {
        get: toUnit, 
        add: function(x, y){
            return toUnit(x).add(toUnit(y)).toString();
        }, 
        sub: function(x, y){
            return toUnit(x).add(toUnit(y)).toString();
        }
    };
})();
