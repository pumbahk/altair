package model;

class ShapeRect extends Shape {

    public function x(d:Float=null):Float {
        return this.attr("x", d);
    }

    public function y(d:Float=null):Float {
        return this.attr("y", d);
    }

    public function width(d:Float=null):Float {
        return this.attr("width", d);
    }

    public function height(d:Float=null):Float {
        return this.attr("height", d);
    }

}