package render.impl;

import model.Shape;
import model.ShapeRect;
import model.ShapePath;
import model.ShapeCircle;

// virtual class
interface RendererImpl {
    public function draw(id:String, shape:Shape, style:Dynamic):Void;
}