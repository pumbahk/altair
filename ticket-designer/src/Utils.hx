class Utils {
    public static function deepcopy<T>(v:T):T {
        switch (Type.typeof(v)) {
        case TUnknown:
            return null;
        case TObject:
            if (Std.is(v, Array)) { 
                var obj = new Array();
                var v_ = cast(v, Array<Dynamic>);
                for (i in 0 ... v_.length)
                    obj.push(deepcopy(v_[i])); 
                return untyped obj; 
            } else {
                var klass = Type.getClass(v);
                if (klass == null) {
                    // anonymous object 
                    var obj: Dynamic = {}; 
                    for (fieldName in Reflect.fields(v)) 
                        Reflect.setField(obj, fieldName, deepcopy(Reflect.field(v, fieldName)));
                    return obj; 
                } else {
                    var obj = Type.createEmptyInstance(Type.getClass(v)); 
                    for (fieldName in Reflect.fields(v))
                        Reflect.setField(obj, fieldName, deepcopy(Reflect.field(v, fieldName))); 
                    return obj;
                }
            }
        case TInt:
            return v;
        case TFloat:
            return v;
        case TBool:
            return v;
        default:
            return v;            
        }
        return null; 
    }

    public static function numberAsStringWithPrec(value:Float, prec:Int):String {
        return untyped __js__('(0. + value)').toFixed(prec);
    }

    public static function pointWithinRect(point:Point, rect:Rect):Bool {
        return point.x >= rect.position.x &&
                point.y >= rect.position.y &&
                point.x < rect.position.x + rect.size.x &&
                point.y < rect.position.y + rect.size.y;
    }

    public static function rectWithinRect(rectA:Rect, rectB:Rect):Bool {
        var rectAbr = { x:rectA.position.x + rectA.size.x,
                        y:rectA.position.y + rectA.size.y };
        return pointWithinRect(rectA.position, rectB) &&
                pointWithinRect(rectAbr, rectB);
    }
}
