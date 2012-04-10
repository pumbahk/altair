package model;

class ShapePath extends Shape {
    public function points(points:Array< Array<Dynamic> >=null):Array< Array<Dynamic> > {
        return this.attr("points", points);
    }
}