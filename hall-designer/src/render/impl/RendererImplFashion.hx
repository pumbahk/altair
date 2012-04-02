package render.impl;

import js.Dom;
import js.Lib;

import fashion.Circle;
import fashion.Drawable;
import fashion.Fashion;
import fashion.Shape;
import fashion.Rect;
import fashion.Path;

import model.ShapeRect;
import model.ShapePath;
import model.ShapeCircle;

import render.Renderer;

class RendererImplFashion implements RendererImpl {

    private static var fashionInitialized:Bool = false;
    private var fas:Fashion;
    private var _tbl:Hash<fashion.Shape>;

    private var _viewport_width:Int;
    private var _viewport_height:Int;
    private var _content_width:Int;
    private var _content_height:Int;
    private var _target:HtmlDom;
    private var _stage:Drawable;
    private var _renderer:Renderer;

    public function new (r:Renderer):Void
    {
        if (!RendererImplFashion.fashionInitialized) {
            Fashion.init(CONF.FASHION_IMPL_PRIORITY);
        }

        this._renderer = r;

        this._viewport_width = 600;
        this._viewport_height = 600;
        this._content_width = 2000;
        this._content_height = 2000;

        this._target = js.Lib.document.getElementById(CONF.FASHION_TARGET_ID);

        this._target.style.width  = this._viewport_width + 'px';
        this._target.style.height = this._viewport_height + 'px';
        this._target.style.border = '1px solid black';

        this._stage = new Drawable(this._target, this._content_width, this._content_height);
        this._tbl   = new Hash<Shape>();
    }

    public function draw(id:String, shape:model.Shape, style:Dynamic):Void
    {
        var real_class:String = Type.getClassName(Type.getClass(shape));

        if (this._tbl.get(id) != null) {
            this._tbl.get(id).style(style);
            return;
        }

        if (real_class == "model.ShapeCircle") {
            this.drawCircle(id, cast shape, style);

        } else if (real_class == "model.ShapeRect") {
            this.drawRect(id, cast shape, style);

        } else if (real_class == "model.ShapePath") {
            this.drawPath(id, cast shape, style);

        } else {
            throw "unexpected class name.";
        }

    }

    public function onMouseOver(id:String):Void {
        this._renderer.onMouseOver(id);
    }
    public function onMouseOut(id:String):Void {
        this._renderer.onMouseOut(id);
    }
    public function onClick(id:String):Void {
        this._renderer.onClick(id);
    }

    private function drawCircle(id:String, shape:ShapeCircle, style:Dynamic):Void
    {
        var circle:Circle = new Circle(shape.x(), shape.y(), shape.r(), shape.r());
        var self = this;

        circle.transform({translate: {x: 50, y:100}});
        circle.addEvent({
            mouseover: function(){self.onMouseOver(id);},
            mouseout: function(){self.onMouseOut(id);},
            click:    function(){self.onClick(id);}
        });


        this._tbl.set(id, circle);

        circle.style(style);
        this._stage.draw(circle);
    }

    private function drawRect(id:String, shape:ShapeRect, style:Dynamic):Void
    {
        var rect:Rect = new Rect(shape.x(), shape.y(), shape.width(), shape.height());
        var self = this;

        rect.transform({translate: {x: 50, y:100}});
        rect.addEvent({
            mouseover: function(){self.onMouseOver(id);},
            mouseout: function(){self.onMouseOut(id);},
            click:    function(){self.onClick(id);}
        });

        this._tbl.set(id, rect);

        rect.style(style);
        this._stage.draw(rect);
    }

    private function drawPath(id:String, shape:ShapePath, style:Dynamic):Void
    {
        var path:Path = new Path(shape.points());
        var self = this;

        path.transform({translate: {x: 50, y:100}});
        path.addEvent({
            mouseover: function(){self.onMouseOver(id);},
            mouseout: function(){self.onMouseOut(id);},
            click:    function(){self.onClick(id);}
        });

        this._tbl.set(id, path);

        path.style(style);
        this._stage.draw(path);
    }
}