package fashion;
import js.Dom;

@:native("Fashion.Drawable")
extern class Drawable {
    public function new        (target:js.HtmlDom, width:Int, height:Int):Void;
    public function findIf     (func:Shape->Bool):Shape;
    public function collectIf  (func:Shape->Bool):Shape;
    public function isExist    (func:Shape->Bool):Bool;
    public function anchor     (d:Dynamic):Dynamic;
    public function draw       (shape:Shape):Shape;
    public function drawAll    (shapes:Array<Shape>):Array<Shape>;
    public function erase      (shape:Shape):Shape;
    public function eraseIf    (func:Shape->Bool):Shape;
    public function eraseAllIf (func:Shape->Bool):Array<Shape>;
}