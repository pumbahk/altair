package model;

class ShapeCircle extends Shape {

    public function x(d:Float=null):Float {
        return this.attr("x", d);
    }

    public function y(d:Float=null):Float {
        return this.attr("y", d);
    }

    public function r(d:Float=null):Float {
        return this.attr("r", d);
    }

}